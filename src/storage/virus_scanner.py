"""Virus scanning service using ClamAV integration."""

import logging
import socket
from typing import BinaryIO, Tuple

logger = logging.getLogger(__name__)

# ClamAV default configuration
DEFAULT_CLAMAV_HOST = "localhost"
DEFAULT_CLAMAV_PORT = 3310
DEFAULT_TIMEOUT = 30  # seconds
CHUNK_SIZE = 4096  # bytes


class ClamAVScanner:
    """ClamAV virus scanner client for file scanning.

    Attributes:
        host: ClamAV daemon hostname
        port: ClamAV daemon port
        timeout: Socket timeout in seconds
    """

    def __init__(
        self,
        host: str = DEFAULT_CLAMAV_HOST,
        port: int = DEFAULT_CLAMAV_PORT,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize ClamAV scanner client.

        Args:
            host: ClamAV daemon hostname or IP address
            port: ClamAV daemon port number
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout

        logger.info(
            "ClamAV scanner initialized",
            extra={
                "host": self.host,
                "port": self.port,
                "timeout": self.timeout,
            },
        )

    def _connect(self) -> socket.socket:
        """Establish connection to ClamAV daemon.

        Returns:
            socket.socket: Connected socket to ClamAV daemon

        Raises:
            ConnectionError: If connection to ClamAV daemon fails
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))

            logger.debug(
                "Connected to ClamAV daemon",
                extra={
                    "host": self.host,
                    "port": self.port,
                },
            )

            return sock

        except socket.timeout:
            logger.error(
                "Connection to ClamAV daemon timed out",
                extra={
                    "host": self.host,
                    "port": self.port,
                    "timeout": self.timeout,
                },
            )
            raise ConnectionError(
                f"Connection to ClamAV at {self.host}:{self.port} timed out"
            )

        except (socket.error, OSError) as e:
            logger.error(
                "Failed to connect to ClamAV daemon",
                extra={
                    "host": self.host,
                    "port": self.port,
                    "error": str(e),
                },
            )
            raise ConnectionError(
                f"Failed to connect to ClamAV at {self.host}:{self.port}: {str(e)}"
            )

    def ping(self) -> bool:
        """Check if ClamAV daemon is available.

        Returns:
            bool: True if ClamAV daemon responds to PING

        Example:
            scanner = ClamAVScanner()
            if scanner.ping():
                print("ClamAV is available")
        """
        try:
            sock = self._connect()
            sock.sendall(b"zPING\0")

            response = sock.recv(256).decode("utf-8").strip()
            sock.close()

            is_available = response == "PONG"

            logger.info(
                "ClamAV ping check",
                extra={
                    "available": is_available,
                    "response": response,
                },
            )

            return is_available

        except (ConnectionError, socket.error, OSError) as e:
            logger.warning(
                "ClamAV ping check failed",
                extra={
                    "error": str(e),
                },
            )
            return False

    def scan_file(self, file: BinaryIO, filename: str) -> Tuple[bool, str]:
        """Scan file for viruses using ClamAV.

        Args:
            file: File-like object to scan
            filename: Original filename for logging

        Returns:
            Tuple[bool, str]: (is_clean, result_message)
                - is_clean: True if no virus detected, False if virus found
                - result_message: Scan result or virus name

        Raises:
            ConnectionError: If ClamAV daemon is unavailable
            TimeoutError: If scan operation times out

        Example:
            scanner = ClamAVScanner()
            with open("document.pdf", "rb") as f:
                is_clean, result = scanner.scan_file(f, "document.pdf")
                if not is_clean:
                    print(f"Virus detected: {result}")
        """
        try:
            logger.info(
                "Starting virus scan",
                extra={
                    "filename": filename,
                },
            )

            sock = self._connect()

            # Send INSTREAM command
            sock.sendall(b"zINSTREAM\0")

            # Read file and send in chunks
            file.seek(0)
            while True:
                chunk = file.read(CHUNK_SIZE)
                if not chunk:
                    break

                # Send chunk size (4 bytes, network byte order) followed by chunk
                size = len(chunk).to_bytes(4, byteorder="big")
                sock.sendall(size + chunk)

            # Send zero-length chunk to signal end of file
            sock.sendall(b"\x00\x00\x00\x00")

            # Receive scan result
            response = sock.recv(1024).decode("utf-8").strip()
            sock.close()

            file.seek(0)  # Reset file position

            # Parse ClamAV response
            # Format: "stream: OK" or "stream: <virus_name> FOUND"
            if "OK" in response:
                logger.info(
                    "File scan completed - clean",
                    extra={
                        "filename": filename,
                        "result": response,
                    },
                )
                return True, "No virus detected"

            elif "FOUND" in response:
                # Extract virus name from response
                parts = response.split(":")
                virus_name = parts[1].strip() if len(parts) > 1 else "Unknown"
                virus_name = virus_name.replace(" FOUND", "")

                logger.warning(
                    "Virus detected in file",
                    extra={
                        "filename": filename,
                        "virus_name": virus_name,
                        "result": response,
                    },
                )
                return False, virus_name

            else:
                logger.error(
                    "Unexpected ClamAV response",
                    extra={
                        "filename": filename,
                        "response": response,
                    },
                )
                raise ValueError(f"Unexpected ClamAV response: {response}")

        except socket.timeout:
            logger.error(
                "Virus scan timed out",
                extra={
                    "filename": filename,
                    "timeout": self.timeout,
                },
            )
            raise TimeoutError(
                f"Virus scan for '{filename}' timed out after {self.timeout} seconds"
            )

        except (ConnectionError, socket.error, OSError) as e:
            logger.error(
                "Virus scan failed due to connection error",
                extra={
                    "filename": filename,
                    "error": str(e),
                },
            )
            raise ConnectionError(
                f"Virus scan failed for '{filename}': {str(e)}"
            )

        except Exception as e:
            logger.error(
                "Unexpected error during virus scan",
                extra={
                    "filename": filename,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            raise

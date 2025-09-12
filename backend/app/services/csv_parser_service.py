# app/services/csv_parser_service.py
"""CSV parsing service for handling file uploads."""

import csv
import io
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class CSVParserService:
    """Handle CSV file parsing and URL extraction."""

    # Common column names for URLs
    URL_COLUMNS = [
        "url",
        "URL",
        "website",
        "Website",
        "domain",
        "Domain",
        "site",
        "Site",
        "web",
        "Web",
        "link",
        "Link",
        "address",
        "Address",
        "webpage",
        "Webpage",
    ]

    @classmethod
    async def parse_csv_file(
        cls, file_content: bytes
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Parse CSV file and extract URLs.

        Args:
            file_content: Raw CSV file content

        Returns:
            Tuple of (urls, errors, headers)
        """
        urls = []
        errors = []
        headers = []

        try:
            # Decode content
            content_str = file_content.decode("utf-8-sig")  # Handle BOM
            csv_reader = csv.DictReader(io.StringIO(content_str))

            # Get headers
            headers = csv_reader.fieldnames or []
            logger.info(f"CSV headers detected: {headers}")

            # Find URL column
            url_column = cls._find_url_column(headers)

            if not url_column and headers:
                # If no standard URL column, try first column
                url_column = headers[0]
                logger.warning(
                    f"No standard URL column found, using first column: {url_column}"
                )

            # Parse rows
            for row_num, row in enumerate(csv_reader, start=1):
                url = cls._extract_url_from_row(row, url_column)

                if url:
                    urls.append(url)
                else:
                    # Try to find URL in any column
                    url_found = False
                    for col_name, col_value in row.items():
                        if col_value and cls._looks_like_url(col_value):
                            urls.append(col_value.strip())
                            url_found = True
                            break

                    if not url_found:
                        errors.append(f"Row {row_num}: No valid URL found")

            logger.info(f"Parsed CSV: {len(urls)} URLs found, {len(errors)} errors")

        except UnicodeDecodeError:
            # Try different encoding
            try:
                content_str = file_content.decode("latin-1")
                return await cls._parse_with_encoding(content_str)
            except Exception as e:
                logger.error(f"CSV encoding error: {e}")
                errors.append("File encoding error - please use UTF-8")
        except Exception as e:
            logger.error(f"CSV parsing error: {e}")
            errors.append(f"Parsing error: {str(e)}")

        return urls, errors, headers

    @classmethod
    def _find_url_column(cls, headers: List[str]) -> str:
        """Find the column containing URLs."""
        for header in headers:
            if header:
                header_lower = header.lower().strip()
                for url_col in cls.URL_COLUMNS:
                    if url_col.lower() in header_lower:
                        return header
        return ""

    @classmethod
    def _extract_url_from_row(cls, row: Dict[str, Any], url_column: str) -> str:
        """Extract URL from a CSV row."""
        if url_column and url_column in row:
            value = row[url_column]
            if value and value.strip():
                return value.strip()

        # Fallback: check common columns
        for col in cls.URL_COLUMNS:
            if col in row and row[col] and row[col].strip():
                return row[col].strip()

        return ""

    @classmethod
    def _looks_like_url(cls, value: str) -> bool:
        """Check if a value looks like a URL."""
        if not value:
            return False

        value = value.strip().lower()
        return "." in value and (
            value.startswith(("http://", "https://", "www."))
            or any(tld in value for tld in [".com", ".org", ".net", ".io", ".co"])
        )

    @classmethod
    async def _parse_with_encoding(
        cls, content_str: str
    ) -> Tuple[List[str], List[str], List[str]]:
        """Parse CSV with specific encoding."""
        urls = []
        errors = []
        headers = []

        csv_reader = csv.DictReader(io.StringIO(content_str))
        headers = csv_reader.fieldnames or []

        for row_num, row in enumerate(csv_reader, start=1):
            for value in row.values():
                if value and cls._looks_like_url(value):
                    urls.append(value.strip())
                    break

        return urls, errors, headers

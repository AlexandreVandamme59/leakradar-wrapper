import httpx
from typing import Any, Dict, Optional, List, Union


class LeakRadarAPIError(Exception):
    """Base exception for API-related errors."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API Error {status_code}: {detail}")


class UnauthorizedError(LeakRadarAPIError):
    """Raised when the user is not authorized to access a resource."""


class ForbiddenError(LeakRadarAPIError):
    """Raised when the user does not have permission (forbidden)."""


class BadRequestError(LeakRadarAPIError):
    """Raised when the request is invalid."""


class TooManyRequestsError(LeakRadarAPIError):
    """Raised when rate limits are exceeded."""


class NotFoundError(LeakRadarAPIError):
    """Raised when the requested resource is not found."""


class ValidationError(LeakRadarAPIError):
    """Raised when the request fails parameter validation."""


class LeakRadarClient:
    """
    An asynchronous client for the LeakRadar.io API.

    Features:
    - Auth via Bearer Token
    - Custom User-Agent
    - Error handling
    - No automatic retries
    - User-friendly methods
    """

    BASE_URL = "https://api.leakradar.io"

    def __init__(
        self,
        token: Optional[str] = None,
        user_agent: str = "LeakRadar-Python-Client/1.0",
        timeout: float = 30.0
    ):
        """
        Initialize the LeakRadarClient.

        :param token: Optional Bearer token for authenticated endpoints.
        :param user_agent: Custom User-Agent to identify usage.
        :param timeout: Request timeout in seconds.
        """
        self.token = token
        self.user_agent = user_agent
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self._default_headers(),
            timeout=timeout
        )

    def _default_headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    async def aclose(self):
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        response = await self._client.request(method, endpoint, **kwargs)
        if response.is_error:
            await self._handle_error(response)
        content_type = response.headers.get("content-type", "")
        # If the response is CSV, return raw bytes
        if "text/csv" in content_type:
            return response.content
        return response.json()

    async def _handle_error(self, response: httpx.Response):
        detail = ""
        try:
            body = response.json()
            detail = body.get("detail", "")
        except Exception:
            detail = response.text

        if response.status_code == 400:
            raise BadRequestError(response.status_code, detail)
        elif response.status_code == 401:
            raise UnauthorizedError(response.status_code, detail)
        elif response.status_code == 403:
            raise ForbiddenError(response.status_code, detail)
        elif response.status_code == 404:
            raise NotFoundError(response.status_code, detail)
        elif response.status_code == 422:
            raise ValidationError(response.status_code, detail)
        elif response.status_code == 429:
            raise TooManyRequestsError(response.status_code, detail)
        else:
            raise LeakRadarAPIError(response.status_code, detail)

    # ---------------------
    # Profile Endpoint
    # ---------------------

    async def get_profile(self) -> Dict[str, Any]:
        """
        Retrieve the authenticated user's profile.
        Requires a valid token.
        """
        return await self._request("GET", "/profile")

    # ---------------------
    # Advanced Search
    # ---------------------

    async def search_advanced(
        self,
        page: int = 1,
        page_size: int = 100,
        show_only_unlocked: bool = False,
        show_only_locked: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        url_domain: Optional[str] = None,
        url_host: Optional[str] = None,
        url_scheme: Optional[str] = None,
        url_port: Optional[int] = None,
        url_tld: Optional[str] = None,
        is_email: Optional[bool] = None,
        email_domain: Optional[str] = None,
        email_host: Optional[str] = None,
        email_tld: Optional[str] = None,
        password_strength: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Perform an advanced search on leaks with multiple filters.
        """
        params = {
            "page": page,
            "page_size": page_size,
            "show_only_unlocked": show_only_unlocked,
            "show_only_locked": show_only_locked,
            "username": username,
            "password": password,
            "url_domain": url_domain,
            "url_host": url_host,
            "url_scheme": url_scheme,
            "url_port": url_port,
            "url_tld": url_tld,
            "is_email": is_email,
            "email_domain": email_domain,
            "email_host": email_host,
            "email_tld": email_tld,
            "password_strength": password_strength
        }
        params = {k: v for k,v in params.items() if v is not None}
        return await self._request("GET", "/search/advanced", params=params)

    async def unlock_all_advanced(
        self,
        filters: Dict[str, Any],
        max_leaks: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Unlock multiple (or all) leaks returned by the same advanced search.
        If max_leaks is not provided, all matched leaks are unlocked.
        """
        params = {}
        if max_leaks is not None:
            params["max"] = max_leaks
        return await self._request("POST", "/search/advanced/unlock", params=params, json=filters)

    async def export_advanced(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        url_domain: Optional[str] = None,
        url_host: Optional[str] = None,
        url_scheme: Optional[str] = None,
        url_port: Optional[int] = None,
        url_tld: Optional[str] = None,
        is_email: Optional[bool] = None,
        email_domain: Optional[str] = None,
        email_host: Optional[str] = None,
        email_tld: Optional[str] = None,
        password_strength: Optional[int] = None
    ) -> bytes:
        """
        Export all unlocked leaks matching the advanced search filters as a CSV file.
        """
        params = {
            "username": username,
            "password": password,
            "url_domain": url_domain,
            "url_host": url_host,
            "url_scheme": url_scheme,
            "url_port": url_port,
            "url_tld": url_tld,
            "is_email": is_email,
            "email_domain": email_domain,
            "email_host": email_host,
            "email_tld": email_tld,
            "password_strength": password_strength
        }
        params = {k: v for k,v in params.items() if v is not None}
        return await self._request("GET", "/search/advanced/export", params=params)

    # ---------------------
    # Domain Endpoints
    # ---------------------

    async def get_domain_report(self, domain: str) -> Dict[str, Any]:
        """Retrieve a domain leak report."""
        return await self._request("GET", f"/search/domain/{domain}")

    async def get_domain_customers(
        self, domain: str,
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None,
        show_only_unlocked: bool = False,
        show_only_locked: bool = False
    ) -> Dict[str, Any]:
        """Get paginated leaks for a domain's customers."""
        params = {
            "page": page,
            "page_size": page_size,
            "search": search,
            "show_only_unlocked": show_only_unlocked,
            "show_only_locked": show_only_locked
        }
        params = {k: v for k,v in params.items() if v is not None}
        return await self._request("GET", f"/search/domain/{domain}/customers", params=params)

    async def get_domain_employees(
        self, domain: str,
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None,
        show_only_unlocked: bool = False,
        show_only_locked: bool = False
    ) -> Dict[str, Any]:
        """Get paginated leaks for a domain's employees."""
        params = {
            "page": page,
            "page_size": page_size,
            "search": search,
            "show_only_unlocked": show_only_unlocked,
            "show_only_locked": show_only_locked
        }
        params = {k: v for k,v in params.items() if v is not None}
        return await self._request("GET", f"/search/domain/{domain}/employees", params=params)

    async def get_domain_third_parties(
        self, domain: str,
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None,
        show_only_unlocked: bool = False,
        show_only_locked: bool = False
    ) -> Dict[str, Any]:
        """Get paginated leaks for a domain's third-party access."""
        params = {
            "page": page,
            "page_size": page_size,
            "search": search,
            "show_only_unlocked": show_only_unlocked,
            "show_only_locked": show_only_locked
        }
        params = {k: v for k,v in params.items() if v is not None}
        return await self._request("GET", f"/search/domain/{domain}/third_parties", params=params)

    async def get_domain_subdomains(
        self, domain: str,
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated subdomains for a domain."""
        params = {
            "page": page,
            "page_size": page_size,
            "search": search
        }
        params = {k: v for k,v in params.items() if v is not None}
        return await self._request("GET", f"/search/domain/{domain}/subdomains", params=params)

    async def export_domain_subdomains(self, domain: str) -> bytes:
        """Export all unique subdomains for a domain as a CSV file."""
        return await self._request("GET", f"/search/domain/{domain}/subdomains/export")

    async def get_domain_urls(
        self, domain: str,
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated URLs for a domain."""
        params = {
            "page": page,
            "page_size": page_size,
            "search": search
        }
        params = {k: v for k,v in params.items() if v is not None}
        return await self._request("GET", f"/search/domain/{domain}/urls", params=params)

    async def export_domain_urls(self, domain: str) -> bytes:
        """Export all unique URLs for a domain as a CSV file."""
        return await self._request("GET", f"/search/domain/{domain}/urls/export")

    async def export_domain_leaks(self, domain: str, leak_type: str, only_usernames: bool = False) -> bytes:
        """
        Export unlocked leaks for a domain and leak_type (employees, customers, or third_parties).
        """
        params = {
            "only_usernames": only_usernames
        }
        return await self._request("GET", f"/search/domain/{domain}/{leak_type}/export", params=params)

    async def unlock_domain_leaks(
        self,
        domain: str,
        leak_type: str,
        search: Optional[str] = None,
        max_leaks: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Unlock all (or limited) leaks for a given domain and leak_type.
        If search is provided, only matching leaks are unlocked.
        """
        params = {}
        if search is not None:
            params["search"] = search
        if max_leaks is not None:
            params["max"] = max_leaks
        return await self._request("POST", f"/search/domain/{domain}/{leak_type}/unlock", params=params)

    # ---------------------
    # Email Endpoints
    # ---------------------

    async def search_email(
        self,
        email: str,
        show_only_unlocked: bool = False,
        show_only_locked: bool = False
    ) -> Dict[str, Any]:
        """
        Search for leaks by email or username.
        Returns a summary and a list of leaks.
        """
        data = {
            "email": email,
            "show_only_unlocked": show_only_unlocked,
            "show_only_locked": show_only_locked
        }
        return await self._request("POST", "/search/email", json=data)

    async def export_email_leaks(self, email: str) -> bytes:
        """
        Export all unlocked leaks for the given email as a CSV file.
        Requires a subscription that allows email export.
        """
        return await self._request("GET", "/search/email/export", params={"email": email})

    async def unlock_email_leaks(
        self,
        email: str,
        show_only_unlocked: bool = False,
        show_only_locked: bool = False,
        max_leaks: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Unlock multiple (or all) leaks associated with an email.
        If max is not provided, all matched leaks are unlocked.
        """
        params = {}
        if max_leaks is not None:
            params["max"] = max_leaks
        data = {
            "email": email,
            "show_only_unlocked": show_only_unlocked,
            "show_only_locked": show_only_locked
        }
        return await self._request("POST", "/search/email/unlock", params=params, json=data)

    # ---------------------
    # Specific Unlock Endpoint
    # ---------------------

    async def unlock_specific_leaks(self, leak_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Unlock a specific list of leaks by their IDs.
        """
        data = {
            "leak_ids": leak_ids
        }
        return await self._request("POST", "/unlock", json=data)

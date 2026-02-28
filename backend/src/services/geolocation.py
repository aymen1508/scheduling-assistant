"""
Geolocation service for getting timezone from IP address
"""

import aiohttp
from datetime import datetime
import pytz
from typing import Optional, Dict, Any

from ..config.logger import log_info, log_warning, log_error


class GeolocationService:
    """Service for retrieving timezone information from IP addresses"""

    @staticmethod
    async def get_timezone_from_ip(ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Get timezone and current time for a user based on their IP address
        
        Args:
            ip_address: User's IP address
            
        Returns:
            Dictionary with timezone, current_time, and formatted time, or None if failed
        """
        try:
            # Skip if localhost
            if ip_address.startswith("127.") or ip_address.startswith("::1"):
                log_info(f"Localhost IP detected ({ip_address}), using UTC")
                return GeolocationService._get_utc_info()
            
            # Use ip-api.com (free tier, no API key needed, 45 requests/minute)
            url = f"http://ip-api.com/json/{ip_address}?fields=timezone,status"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "success":
                            timezone_str = data.get("timezone")
                            if timezone_str:
                                log_info(f"Geo-IP lookup successful for {ip_address}: {timezone_str}")
                                return GeolocationService._get_timezone_info(timezone_str)
                        
                        log_warning(f"IP API failed for {ip_address}: {data.get('message', 'unknown error')}")
                    else:
                        log_warning(f"IP API returned status {response.status}")
                        
        except asyncio.TimeoutError:
            log_warning(f"Geo-IP lookup timeout for {ip_address}")
        except Exception as e:
            log_warning(f"Geo-IP lookup failed for {ip_address}: {e}")
        
        # Fallback to UTC
        log_info("Falling back to UTC timezone")
        return GeolocationService._get_utc_info()
    
    @staticmethod
    async def get_timezone_info(timezone_str: str) -> Dict[str, Any]:
        """
        Get timezone info for a given timezone name
        
        Args:
            timezone_str: Timezone name (e.g., 'America/New_York')
            
        Returns:
            Dictionary with timezone, current_time, and formatted time
        """
        return GeolocationService._get_timezone_info(timezone_str)
    
    @staticmethod
    def _get_timezone_info(timezone_str: str) -> Dict[str, Any]:
        """Get current time in a specific timezone"""
        try:
            tz = pytz.timezone(timezone_str)
            local_time = datetime.now(tz)
            
            return {
                "timezone": timezone_str,
                "timezone_offset": local_time.strftime("%z"),
                "current_time": local_time.strftime("%Y-%m-%d %H:%M:%S"),
                "current_time_formatted": local_time.strftime("%A, %B %d, %Y at %I:%M %p %Z"),
                "utc_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            }
        except Exception as e:
            log_warning(f"Failed to get timezone info for {timezone_str}: {e}")
            return GeolocationService._get_utc_info()
    
    @staticmethod
    def _get_utc_info() -> Dict[str, Any]:
        """Get current time in UTC"""
        utc_time = datetime.utcnow()
        return {
            "timezone": "UTC",
            "timezone_offset": "+0000",
            "current_time": utc_time.strftime("%Y-%m-%d %H:%M:%S"),
            "current_time_formatted": utc_time.strftime("%A, %B %d, %Y at %I:%M %p UTC"),
            "utc_time": utc_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        }


# Make asyncio available
import asyncio

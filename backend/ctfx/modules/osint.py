import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

class OSINTAnalyzer:
    """OSINT engine extracting geolocation clues, EXIF camera details, and document metadata."""

    @classmethod
    def _convert_dms_to_decimal(cls, dms_tuple, ref: str) -> Optional[float]:
        """Convert GPS Degree-Minute-Second tuple to signed decimal degrees."""
        try:
            degrees = float(dms_tuple[0])
            minutes = float(dms_tuple[1])
            seconds = float(dms_tuple[2])
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            if ref.upper() in ("S", "W"):
                decimal = -decimal
            return round(decimal, 6)
        except Exception:
            return None

    @classmethod
    def extract_exif(cls, file_path: Path) -> Dict[str, Any]:
        """Extract camera hardware, timestamps, and GPS coordinates with map deep links."""
        metadata = {}
        gps_data = {}
        lat_dec = None
        lon_dec = None

        try:
            with Image.open(file_path) as img:
                exif = img.getexif()
                if not exif:
                    return {"has_exif": False, "note": "No EXIF metadata present in image"}

                for tag_id, value in exif.items():
                    tag_name = TAGS.get(tag_id, f"Tag_{tag_id}")
                    if tag_name == "GPSInfo":
                        for t in value:
                            sub_tag = GPSTAGS.get(t, f"GPSTag_{t}")
                            gps_data[sub_tag] = value[t]
                    elif isinstance(value, (str, int, float)):
                        metadata[tag_name] = value

                # Convert GPS if present
                if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
                    lat_dec = cls._convert_dms_to_decimal(gps_data["GPSLatitude"], gps_data["GPSLatitudeRef"])
                if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
                    lon_dec = cls._convert_dms_to_decimal(gps_data["GPSLongitude"], gps_data["GPSLongitudeRef"])

        except Exception as e:
            return {"has_exif": False, "error": f"EXIF extraction error: {str(e)}"}

        maps_links = {}
        if lat_dec is not None and lon_dec is not None:
            maps_links = {
                "google_maps": f"https://www.google.com/maps?q={lat_dec},{lon_dec}",
                "openstreetmap": f"https://www.openstreetmap.org/?mlat={lat_dec}&mlon={lon_dec}#map=16/{lat_dec}/{lon_dec}"
            }

        return {
            "has_exif": True,
            "camera_metadata": metadata,
            "raw_gps": {k: str(v) for k, v in gps_data.items()},
            "coordinates": {
                "latitude": lat_dec,
                "longitude": lon_dec,
            } if lat_dec and lon_dec else None,
            "map_links": maps_links
        }

    @classmethod
    def extract_pdf_metadata(cls, file_path: Path) -> Dict[str, Any]:
        """Extract document provenance from PDF files."""
        try:
            import pypdf
            reader = pypdf.PdfReader(str(file_path))
            info = reader.metadata
            if not info:
                return {"has_metadata": False, "note": "No PDF metadata block"}

            doc_meta = {}
            for k, v in info.items():
                clean_k = k.lstrip("/")
                doc_meta[clean_k] = str(v)

            return {
                "has_metadata": True,
                "pages": len(reader.pages),
                "metadata": doc_meta
            }
        except Exception as e:
            return {"has_metadata": False, "error": f"PDF metadata error: {str(e)}"}

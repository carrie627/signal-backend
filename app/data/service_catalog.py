from typing import TypedDict


class ServiceCatalogEntry(TypedDict):
    name: str
    description: str


# Replace this with the real client's service list per project. Descriptions
# matter more than names for match quality — write them the way a lead would
# describe their problem, not the way a brochure would describe the service.
SERVICE_CATALOG: list[ServiceCatalogEntry] = [
    {
        "name": "Web design",
        "description": (
            "Building or rebuilding a website, improving mobile conversion, "
            "redesigning a slow or outdated site, landing page creation."
        ),
    },
    {
        "name": "SEO audit",
        "description": (
            "Search ranking dropped, organic traffic declining, need "
            "technical or local SEO review and recommendations."
        ),
    },
    {
        "name": "Brand identity",
        "description": (
            "New logo, visual identity, rebranding, brand guidelines for a "
            "launch or repositioning."
        ),
    },
    {
        "name": "Social media management",
        "description": (
            "Ongoing management of Instagram, LinkedIn, or other social "
            "accounts, content calendars, community engagement."
        ),
    },
    {
        "name": "Paid ads management",
        "description": (
            "Running or optimizing Meta, Google, or other paid ad "
            "campaigns, improving cost per lead or return on ad spend."
        ),
    },
]

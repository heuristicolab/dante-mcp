# manifest_hash: 573c978f422e5c379830c2736505b260b93186f28715b081388ec45acccfd1ac
"""
dante_mcp — Official Model Context Protocol (MCP) Connector for Dante IX (https://danteix.com).
"""
from .client import (
    MCP_CLEANROOM_RELEASE_V1_MANIFEST_HASH,
    MCP_EDGE_V1_MANIFEST_HASH,
    MCP_PRIVACY_SHIELD_V1_MANIFEST_HASH,
    MCP_TOOLS_SCHEMA,
    DanteMcpThinClient,
    main,
)

__version__ = "2.1.0"
__all__ = [
    "DanteMcpThinClient",
    "MCP_CLEANROOM_RELEASE_V1_MANIFEST_HASH",
    "MCP_EDGE_V1_MANIFEST_HASH",
    "MCP_PRIVACY_SHIELD_V1_MANIFEST_HASH",
    "MCP_TOOLS_SCHEMA",
    "__version__",
    "main",
]

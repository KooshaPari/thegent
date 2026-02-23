"""WP-13001: P2P Agent Discovery and Peer-to-Peer Orchestration."""

import orjson as json
import logging
import socket
import threading
import time

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class PeerAgent(BaseModel):
    """Metadata for a peer agent on the network."""

    agent_id: str
    host: str
    port: int
    capabilities: list[str]
    last_seen: float
    load_score: float = 0.0  # WP-13002
    trust_score: float = 1.0  # WP-13002


class P2PDiscovery:
    """Zeroconf-style discovery for agents on the local network."""

    def __init__(self, agent_id: str, port: int, capabilities: list[str]) -> None:
        self.agent_id = agent_id
        self.port = port
        self.capabilities = capabilities
        self.peers: dict[str, PeerAgent] = {}
        self._stop_event = threading.Event()
        self.broadcast_port = 38470  # thegent default broadcast port

    def start(self):
        """Start discovery and heartbeat threads."""
        self._stop_event.clear()
        threading.Thread(target=self._broadcast_heartbeat, daemon=True).start()
        threading.Thread(target=self._listen_for_peers, daemon=True).start()

    def stop(self):
        self._stop_event.set()

    def _broadcast_heartbeat(self):
        """Broadcast availability to local network with capabilities."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        msg = json.dumps(
            {
                "agent_id": self.agent_id,
                "port": self.port,
                "capabilities": self.capabilities,
                "type": "heartbeat",
                "load_score": 0.2,  # Added for WP-13002
                "trust_score": 0.9,  # Added for WP-13002
            }
        ).encode()

        while not self._stop_event.is_set():
            try:
                sock.sendto(msg, ("<broadcast>", self.broadcast_port))
            except Exception as e:
                _log.debug("Heartbeat broadcast failed: %s", e)
            time.sleep(10)

    def _listen_for_peers(self):
        """Listen for heartbeats from other agents."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.broadcast_port))
        sock.settimeout(1.0)

        while not self._stop_event.is_set():
            try:
                data, addr = sock.recvfrom(1024)
                peer_data = json.loads(data.decode())
                if peer_data.get("agent_id") == self.agent_id:
                    continue

                peer = PeerAgent(
                    agent_id=peer_data["agent_id"],
                    host=addr[0],
                    port=peer_data["port"],
                    capabilities=peer_data["capabilities"],
                    last_seen=time.time(),
                    load_score=peer_data.get("load_score", 0.0),
                    trust_score=peer_data.get("trust_score", 1.0),
                )
                self.peers[peer.agent_id] = peer
                _log.info("Discovered peer: %s at %s", peer.agent_id, peer.host)
            except TimeoutError:
                continue
            except Exception as e:
                _log.debug("Peer discovery error: %s", e)

    def list_peers(self) -> list[PeerAgent]:
        """Return list of active peers (seen in last 30s)."""
        now = time.time()
        return [p for p in self.peers.values() if now - p.last_seen < 30]

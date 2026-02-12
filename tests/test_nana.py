from nana.brain import NanaBrain
from nana.memory import MemoryStore


def test_starts_nearly_empty(tmp_path):
    store = MemoryStore.load(tmp_path / "memory.json")
    brain = NanaBrain(store)

    assert store.brain_state["neurons"] == {}
    reply = brain.respond("")
    assert "newly awake" in reply.lower() or "beginning" in reply.lower()


def test_brain_grows_with_interactions(tmp_path):
    store = MemoryStore.load(tmp_path / "memory.json")
    brain = NanaBrain(store)

    brain.respond("I code late at night and build games")
    brain.respond("I love creative flow and focus")

    neurons = store.brain_state["neurons"]
    assert len(neurons) >= 6
    assert "night" in neurons
    assert neurons["night"]["hits"] >= 1


def test_persistence_keeps_growth(tmp_path):
    path = tmp_path / "memory.json"
    store = MemoryStore.load(path)
    brain = NanaBrain(store)

    brain.respond("I explore robotics and embedded systems")
    store.save()

    reloaded = MemoryStore.load(path)
    assert "robotics" in reloaded.brain_state["neurons"]

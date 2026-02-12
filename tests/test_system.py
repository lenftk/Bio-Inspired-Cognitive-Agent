#!/usr/bin/env python3
import asyncio
import logging
import sys
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

try:
    from core.hormone_system import HormoneModulator, AgentState
    from core.memory_system import ContextManager, ProfileManager
    from core.chroma_store import ChromaStore
    logger.info("✓ All modules imported successfully")
except Exception as e:
    logger.error(f"✗ Import failed: {e}")
    sys.exit(1)

def test_hormone_system():
    logger.info("\n" + "="*30 + " Hormone System " + "="*30)
    hormone_sys = HormoneModulator()
    state = hormone_sys.get_state()
    logger.info(f"Initial state: {state}")
    assert state['stress'] == 0.1 and state['reward'] == 0.5 and state['stability'] == 0.7
    
    s_d, r_d, st_d = hormone_sys.evaluate_state(-0.8)
    hormone_sys.update_hormones(s_d, r_d, st_d)
    assert hormone_sys.stress > 0.5
    
    s_d, r_d, st_d = hormone_sys.evaluate_state(0.9)
    hormone_sys.update_hormones(s_d, r_d, st_d)
    assert hormone_sys.reward > 0.7
    
    for _ in range(5): hormone_sys.update_hormones(0, 0, 0)
    logger.info(f"State after decay: {hormone_sys.get_state()}")
    
    suggested = hormone_sys.suggest_state_transition()
    logger.info(f"Suggested state: {suggested.value}")
    logger.info("✓ Hormone system test PASSED\n")
    return True

def test_memory_system():
    logger.info("="*30 + " Memory System " + "="*30)
    try:
        memory_ctx = ContextManager(use_chroma=True, chroma_persist_dir="chroma_db_test")
        logger.info(f"Using backend: {memory_ctx._using}")
        memory_ctx.add_to_buffer("User", "Hello")
        memory_ctx.add_to_buffer("Agent", "Hi")
        assert len(memory_ctx.buffer) == 2, f"Buffer size mismatch: {len(memory_ctx.buffer)}"
        
        if memory_ctx._using == "chroma":
            from sentence_transformers import SentenceTransformer
            encoder = SentenceTransformer('all-MiniLM-L6-v2')
            doc = "The user likes Python"
            emb = encoder.encode(doc).tolist()
            memory_ctx.db.add_memory(doc, emb, source="test")
            logger.info("Added test memory to Chroma")
            
            results = memory_ctx.retrieve_relevant("What does the user like?", top_k=1)
            assert len(results) > 0, "No results found in Chroma"
        
        logger.info("✓ Memory system test PASSED\n")
        return True
    except Exception as e:
        logger.error(f"✗ Memory system test FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chroma_store():
    logger.info("="*30 + " Chroma Store " + "="*30)
    try:
        db = ChromaStore(persist_directory="chroma_db_test", collection_name="test_collection")
        db.add_memory("Test document", [0.1] * 384, source="test")
        results = db.query([0.1] * 384, top_k=1)
        assert len(results) > 0
        logger.info("✓ Chroma store test PASSED\n")
        return True
    except Exception as e:
        logger.error(f"✗ Chroma store test FAILED: {e}")
        return False

def test_profile_manager():
    logger.info("="*30 + " Profile Manager " + "="*30)
    try:
        profile = ProfileManager(filepath="profile_test.json")
        profile.add_fact("likes Python")
        assert "likes Python" in profile.data["facts"]
        logger.info(f"Core prompt: {profile.get_core_prompt()}")
        logger.info("✓ Profile manager test PASSED\n")
        return True
    except Exception as e:
        logger.error(f"✗ Profile manager test FAILED: {e}")
        return False

def main():
    results = {
        "Hormone System": test_hormone_system(),
        "Memory System": test_memory_system(),
        "Chroma Store": test_chroma_store(),
        "Profile Manager": test_profile_manager()
    }
    passed = sum(1 for v in results.values() if v)
    for name, res in results.items():
        logger.info(f"{name}: {'✓ PASSED' if res else '✗ FAILED'}")
    logger.info(f"\nTotal: {passed}/{len(results)} tests passed")
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())

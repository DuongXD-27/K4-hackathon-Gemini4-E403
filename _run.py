import sys
sys.path.insert(0, r'f:\K4-hackathon-Gemini4-E403')
try:
    import _fix_helper
    print("Helper loaded")
except ImportError:
    print("No helper yet")

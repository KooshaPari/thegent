def test_import():
    import thegent
    print(f"thegent file: {thegent.__file__}")
    from thegent import crew
    print(f"crew file: {crew.__file__}")

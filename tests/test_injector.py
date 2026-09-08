from talk_to_write.injector import TextInjector

def test_injector_clipboard():
    injector = TextInjector()
    test_str = "Talk-to-Write Test String 123"
    assert injector.set_clipboard(test_str) is True
    assert injector.get_current_clipboard() == test_str

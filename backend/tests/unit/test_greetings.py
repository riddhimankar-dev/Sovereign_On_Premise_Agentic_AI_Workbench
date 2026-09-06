import pytest

from app.agents.greetings import is_greeting, fast_path_response


class TestGreetingClassification:
    @pytest.mark.parametrize("query", [
        "Hello",
        "hello",
        "Hi there",
        "Hey, good morning",
        "thanks!",
        "thank you",
        "how are you?",
        "goodbye",
        "who are you?",
        "ok",
    ])
    def test_recognized_greetings(self, query):
        assert is_greeting(query) is True, f"should classify as greeting: {query}"

    @pytest.mark.parametrize("query", [
        "What is the maximum operating pressure for P-102?",
        "Create an approval note for the overpressure assessment.",
        "Analyze the latest P-102 inspection data",
        "What is the corrosion rate?",
        "Write Python code to compute the deviation",
        "How do I create a report?",
    ])
    def test_subject_queries_are_not_greetings(self, query):
        assert is_greeting(query) is False, f"should NOT classify as greeting: {query}"


class TestFastPathResponse:
    @pytest.mark.parametrize("query", ["hi", "hello", "hey", "yo", "hi there", "hello there"])
    def test_common_greetings_get_fast_reply(self, query):
        resp = fast_path_response(query)
        assert resp is not None
        assert "reply" in resp

    def test_empty_query_no_fast_reply(self):
        assert fast_path_response("") is None

    def test_greeting_with_subject_falls_through(self):
        assert fast_path_response("Hello, what is the pressure for P-102?") is None

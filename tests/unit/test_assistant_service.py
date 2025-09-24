from src.agent.models.packing_models import PackingContext
from src.agent.services.assistant_service import PackingAssistantService


def make_context():
    return PackingContext(
        destination="Rome",
        trip_length_days=2,
        activities=["museum"],
        time_of_day_usage=["day", "night"],
    )


def test_chat_once_returns_reply():
    service = PackingAssistantService.create()
    response = service.chat_once("What should I bring?", make_context())

    assert "DeepseekTravels" in response
    assert "Socks" in response or "Baseline" in response


from src.agent.models.packing_models import PackingContext
from src.agent.services.assistant_service import PackingAssistantService


def make_context():
    return PackingContext(
        destination="Rome",
        trip_length_days=2,
        activities=["museum"],
        time_of_day_usage=["day", "night"],
        origin_city="Warsaw",
        destination_country="Italy",
        nationality="Polish",
        start_date="2025-10-01",
        traveling_adults=1,
        carrying_children=0,
        carrying_infants=0,
        traveling_pets=0,
    )


def test_chat_once_returns_reply():
    service = PackingAssistantService.create()
    response = service.chat_once(message="What should I bring?", context=make_context(), callbacks=None)

    assert response


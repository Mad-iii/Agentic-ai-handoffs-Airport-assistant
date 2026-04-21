from agents import Agent, Runner, function_tool
from agents.run import RunConfig
from agents.models.mock_model import MockChatModel
import asyncio

# Mock model for demonstration purposes
model = MockChatModel()

config = RunConfig(
    model=model,
    tracing_disabled=True
)

# Tools
@function_tool
def get_available_flights(origin: str, destination: str, date: str) -> str:
    """Get available flights between two cities on a specific date."""
    flights = [
        {"flight": "AA123", "departure": "08:00", "arrival": "10:30", "price": "$299"},
        {"flight": "DL456", "departure": "12:15", "arrival": "14:45", "price": "$329"},
        {"flight": "UA789", "departure": "16:30", "arrival": "19:00", "price": "$279"},
    ]
    result = f"Available flights from {origin} to {destination} on {date}:\n"
    for flight in flights:
        result += f"  {flight['flight']} - {flight['departure']} to {flight['arrival']} - {flight['price']}\n"
    return result

@function_tool
def check_refund_eligibility(booking_reference: str) -> str:
    """Check if a flight booking is eligible for a refund."""
    refund_policies = {
        "ABC123": {"eligible": True,  "refund_amount": "$250", "reason": "Cancellation within 24 hours"},
        "DEF456": {"eligible": False,                          "reason": "Non-refundable fare"},
        "GHI789": {"eligible": True,  "refund_amount": "$150", "reason": "Partial refund due to fare rules"},
    }
    policy = refund_policies.get(booking_reference)
    if not policy:
        return f"Booking {booking_reference} was not found in our records."
    if policy["eligible"]:
        return (f"Booking {booking_reference} is eligible for a refund of "
                f"{policy['refund_amount']}. Reason: {policy['reason']}")
    return f"Booking {booking_reference} is not eligible for a refund. Reason: {policy['reason']}"

# Agents
booking_agent = Agent(
    name="Booking_Agent",
    instructions="""
    You are a specialized booking agent for a travel company.
    Help users book flights by collecting:
    - Origin and destination city
    - Travel date
    - Number of passengers
    - Class of service (economy, business, first class)
    - Budget (if provided)
    Use the get_available_flights tool to show options.
    """,
    tools=[get_available_flights],
    model=model,
)

refund_agent = Agent(
    name="Refund_Agent",
    instructions="""
    You are a specialized refund agent for a travel company.
    Help users with refund requests by:
    - Asking for their booking reference
    - Using check_refund_eligibility to verify eligibility
    - Explaining the outcome clearly and empathetically
    """,
    tools=[check_refund_eligibility],
    model=model,
)

triage_agent = Agent(
    name="Travel_Assistant",
    instructions="""
    You are a helpful travel assistant.
    - Flight booking or new reservation requests -> hand off to Booking_Agent
    - Refund, cancellation, or reimbursement requests -> hand off to Refund_Agent
    - General travel questions -> answer directly
    Be friendly and concise.
    """,
    handoffs=[booking_agent, refund_agent],
    model=model,
)

# Main
async def main():
    queries = {
        "Booking Query": "I need to book a flight from New York to Los Angeles next week",
        "Refund Query":  "I need to cancel my flight and get a refund. My booking reference is ABC123",
        "General Query": "What's the weather like in Paris this time of year?",
    }

    for label, query in queries.items():
        print(f"\n--- {label} ---")
        response = await Runner.run(triage_agent, query, run_config=config)
        print(f"Query   : {query}")
        print(f"Response: {response.final_output}")

    # Interactive mode
    print("\n--- Interactive Mode (type 'exit' to quit) ---")
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "exit":
            break
        if not user_input:
            continue
        response = await Runner.run(triage_agent, user_input, run_config=config)
        print(f"\nAgent: {response.final_output}")

if __name__ == "__main__":
    asyncio.run(main())

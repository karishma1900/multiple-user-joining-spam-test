import random
import time
from aiogram import Bot, Dispatcher, types
from collections import defaultdict, deque
import asyncio

API_TOKEN = "8104261349:AAFJiEaNsGWeIuM1bGErug-8l_wuViwOFPg"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Variables for join tracking
recent_joins = defaultdict(lambda: deque())
JOIN_THRESHOLD = 5
TIME_WINDOW = 10  # 10 seconds

# Simulate a user joining
async def simulate_user_join(chat_id: int, user_id: int):
    event = types.ChatMemberUpdated(
        chat=types.Chat(id=chat_id, type="supergroup"),
        from_user=types.User(id=user_id, first_name=f"Test User {user_id}", is_bot=False),
        old_chat_member=None,
        new_chat_member=types.ChatMember(
            user=types.User(id=user_id, first_name=f"Test User {user_id}", is_bot=False),
            status="member"
        )
    )
    await handle_new_chat_members(event)

# Simulate multiple users joining
async def simulate_mass_join(chat_id: int, num_users: int):
    user_ids = [random.randint(100000, 999999) for _ in range(num_users)]  # Generate random user IDs
    for user_id in user_ids:
        await simulate_user_join(chat_id, user_id)

# Actual logic to handle multiple joins
@dp.chat_member()
async def handle_new_chat_members(event: types.ChatMemberUpdated):
    chat_id = event.chat.id
    if event.old_chat_member.status in {"left", "kicked"} and event.new_chat_member.status == "member":
        now = time.time()
        user_id = event.new_chat_member.user.id
        recent_joins[chat_id].append((now, user_id))

        # Remove joins older than the time window
        while recent_joins[chat_id] and now - recent_joins[chat_id][0][0] > TIME_WINDOW:
            recent_joins[chat_id].popleft()

        # If too many joins in short time, ban them all
        if len(recent_joins[chat_id]) >= JOIN_THRESHOLD:
            for _, uid in recent_joins[chat_id]:
                await bot.ban_chat_member(chat_id, uid)
                print(f"Banned user {uid} for join spam.")

            # Notify the group
            await bot.send_message(chat_id, "⚠️ Join spam detected. Recent new users have been banned.")

            # Clear queue after action
            recent_joins[chat_id].clear()

# Running the test
async def main():
    # Replace this with your actual public group username
    group_username = '@helogrouo'

    # Get the chat ID of the public group using its username
    chat = await bot.get_chat(group_username)
    chat_id = chat.id

    # Simulate 10 users joining at once to test the join spam logic
    num_users = 10
    await simulate_mass_join(chat_id, num_users)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

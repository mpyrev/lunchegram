from typing import Optional

from core.utils import get_redis


class NoStateException(Exception):
    pass


def _make_state_key(user_id):
    return f'state:{user_id}'


class StateRegistry:
    def __init__(self, state_ttl=24*60*60):
        self._handlers = {}
        self.redis = get_redis()
        self.state_ttl = state_ttl

    def register(self, state_name: str):
        def registrator(func):
            self._handlers[state_name] = func
            return func
        return registrator

    def process_message(self, message):
        state = self._get_state(message.from_user.id)
        if state is None:
            raise NoStateException
        assert state in self._handlers, f'Registered handler for state `{state}` not found'
        self._handlers[state](message)

    def _get_state(self, user_id) -> Optional[str]:
        state_key = _make_state_key(user_id)
        state = self.redis.get(state_key)
        return state.decode('utf-8') if state else state

    def set_state(self, user_id, new_state):
        state_key = _make_state_key(user_id)
        self.redis.set(state_key, new_state, ex=self.state_ttl)

    def del_state(self, user_id):
        state_key = _make_state_key(user_id)
        self.redis.delete(state_key)


state_registry = StateRegistry()

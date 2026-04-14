import uuid

class Message:
    def __init__(self, sender_id: str, receiver_id: str | None, content: str, metadata: dict | None = None):
        self.message_id = str(uuid.uuid4())
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.metadata = metadata if metadata else {}

    def __str__(self):
        return f"Message(id={self.message_id[:6]}..., sender={self.sender_id[:6]}..., receiver={self.receiver_id[:6] if self.receiver_id else 'ALL'}, content='{self.content[:50]}...')"

    def __repr__(self):
        return str(self)

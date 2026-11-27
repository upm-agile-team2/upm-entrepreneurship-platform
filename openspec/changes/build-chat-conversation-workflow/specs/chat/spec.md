# Spec Delta

## Purpose

Lets authenticated platform users start conversations, exchange messages, and return to their message history through a chat interface.

## ADDED Requirements

### Requirement: Reuse a conversation for the same pair
The system SHALL create a conversation with exactly two participants when no conversation exists for the selected pair, and SHALL reuse the existing conversation for that pair.

Source: US029 (#100)

#### Scenario: Start a conversation with a new participant
- **WHEN** an authenticated user starts a conversation with another user and no conversation exists for the pair
- **THEN** one conversation is created with those two participants

#### Scenario: Return to an existing conversation
- **WHEN** an authenticated user starts a conversation with someone they already have a conversation with
- **THEN** the existing conversation is returned and no duplicate is created

### Requirement: Restrict conversations to their participants
The system SHALL allow only a conversation's participants to view its messages or send messages to it.

Source: US029 (#100)

#### Scenario: Non-participant requests a conversation
- **WHEN** an authenticated user who is not a participant requests a conversation or its messages
- **THEN** the conversation is not disclosed and no message is sent

### Requirement: Send a non-empty message
The system SHALL save a non-empty message from a conversation participant with its conversation, sender, text, and send time.

Source: US029 (#100)

#### Scenario: Participant sends a valid message
- **WHEN** a conversation participant submits a message containing non-whitespace text
- **THEN** the message is saved in that conversation and identifies the sender and send time

#### Scenario: Participant submits an empty message
- **WHEN** a conversation participant submits a message with no text or only whitespace
- **THEN** no message is saved and the interface explains that text is required

### Requirement: Display a participant's conversations and message history
The system SHALL display a user's conversations and show each selected conversation's messages in chronological order with sender information.

Source: US029 (#100)

#### Scenario: Open the conversation list
- **WHEN** an authenticated user opens chat
- **THEN** the platform displays only conversations in which that user participates

#### Scenario: Open a conversation thread
- **WHEN** a participant selects one of their conversations
- **THEN** the platform displays its messages from earliest to latest with the sender for each message

#### Scenario: User has no conversations
- **WHEN** an authenticated user opens chat and has no conversations
- **THEN** the platform displays a clear empty state

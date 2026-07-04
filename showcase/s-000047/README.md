# Prompt Typing To Panel Transform

This showcase recreates a prompt input animation:

- A long prompt bar types `Write a simple if loop in C`.
- The send button fades out as the bar expands.
- The prompt transforms into a large rounded panel with a small final prompt label and loading dots.

The typing effect uses multiple fixed `Text` nodes with opacity windows, keeping the DSL parser-friendly and UI-editable.

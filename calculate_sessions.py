import sys
import re
from collections import defaultdict
from typing import List, Tuple, Dict

# Used AI to generate this REGEX
LOG_REGEX = re.compile(r"^(\d{2}:\d{2}:\d{2})\s+([\w\d]+)\s+(Start|End)$")


def time_to_seconds(time_str: str) -> int:
    hours, minutes, seconds = map(int, time_str.split(":"))
    return (hours * 3600) + (minutes * 60) + seconds


def calculate_sessions(filepath: str):
    all_events: List[Tuple[int, str, str]] = []

    try:
        with open(filepath, "r") as f:
            for log in f:
                match = LOG_REGEX.match(log.strip())
                if match:
                    time_str, username, action = match.groups()
                    seconds = time_to_seconds(time_str)
                    all_events.append((seconds, username, action))

    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)

    if not all_events:
        print("No valid log entries found.")
        return

    earliest_time = all_events[0][0]
    latest_time = all_events[-1][0]

    user_total_duration: Dict[str, int] = defaultdict(int)
    user_sessions: Dict[str, int] = defaultdict(int)
    user_start_times: Dict[str, List[int]] = defaultdict(list)

    for seconds, username, action in all_events:
        if action == "Start":
            user_start_times[username].append(seconds)

        elif action == "End":
            user_sessions[username] += 1

            if user_start_times[username]:
                start_time = user_start_times[username].pop()
                duration = seconds - start_time
                user_total_duration[username] += duration
            else:
                start_time = earliest_time
                duration = seconds - start_time
                user_total_duration[username] += duration

    for username, starts in user_start_times.items():
        for start_time in starts:
            user_sessions[username] += 1

            end_time = latest_time
            duration = end_time - start_time
            user_total_duration[username] += duration

    for user in sorted(user_total_duration.keys()):
        print(f"{user} {user_sessions[user]} {user_total_duration[user]}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python calculate_sessions.py <path_to_log_file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    calculate_sessions(filepath)


if __name__ == "__main__":
    main()

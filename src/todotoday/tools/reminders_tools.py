import threading

import EventKit
import Foundation


def get_pending_reminders() -> str:
    """Get all pending (incomplete) reminders from Apple Reminders."""
    store = EventKit.EKEventStore.alloc().init()

    # Request access (async API — block with threading event)
    access = {"granted": False}
    access_done = threading.Event()

    def access_handler(granted, error):
        access["granted"] = granted
        access_done.set()

    store.requestFullAccessToRemindersWithCompletion_(access_handler)
    access_done.wait(timeout=10)

    if not access["granted"]:
        return "Error: Reminders access not granted. Check System Settings > Privacy & Security > Reminders."

    predicate = store.predicateForIncompleteRemindersWithDueDateStarting_ending_calendars_(
        None, None, None
    )

    # fetchRemindersMatchingPredicate is async — use a threading event to wait
    results = []
    done_event = threading.Event()

    def completion(reminders):
        if reminders:
            results.extend(reminders)
        done_event.set()

    store.fetchRemindersMatchingPredicate_completion_(predicate, completion)
    done_event.wait(timeout=60)

    if not results:
        return "No pending reminders found."

    fmt = Foundation.NSDateFormatter.alloc().init()
    fmt.setDateFormat_("yyyy-MM-dd")

    lines = []
    for reminder in results:
        list_name = str(reminder.calendar().title())
        title = str(reminder.title()) if reminder.title() else ""
        priority = reminder.priority()

        due_date_str = "No due date"
        due_components = reminder.dueDateComponents()
        if due_components:
            date = Foundation.NSCalendar.currentCalendar().dateFromComponents_(due_components)
            if date:
                due_date_str = str(fmt.stringFromDate_(date))

        entry = f"[{list_name}] {title} (due: {due_date_str})"
        if priority and priority != 0:
            entry += f" [priority: {priority}]"
        lines.append(entry)

    return f"Pending reminders ({len(lines)}):\n" + "\n".join(lines)

import threading

import EventKit  # pyobjc-framework-EventKit
import Foundation


def _request_calendar_access(store):
    """Request full calendar access, blocking until granted or denied."""
    result = {"granted": False}
    done = threading.Event()

    def handler(granted, error):
        result["granted"] = granted
        done.set()

    store.requestFullAccessToEventsWithCompletion_(handler)
    done.wait(timeout=10)
    return result["granted"]


def get_todays_calendar_events() -> str:
    """Get all calendar events scheduled for today from Apple Calendar."""
    store = EventKit.EKEventStore.alloc().init()

    if not _request_calendar_access(store):
        return "Error: Calendar access not granted. Check System Settings > Privacy & Security > Calendars."

    calendar = Foundation.NSCalendar.currentCalendar()
    now = Foundation.NSDate.date()
    start_of_day = calendar.startOfDayForDate_(now)
    end_of_day = calendar.dateByAddingUnit_value_toDate_options_(
        Foundation.NSCalendarUnitDay, 1, start_of_day, 0
    )

    predicate = store.predicateForEventsWithStartDate_endDate_calendars_(
        start_of_day, end_of_day, None
    )
    events = store.eventsMatchingPredicate_(predicate)

    if not events or len(events) == 0:
        return "No calendar events found for today."

    fmt = Foundation.NSDateFormatter.alloc().init()
    fmt.setDateFormat_("HH:mm")

    lines = []
    for event in events:
        cal_name = str(event.calendar().title())
        title = str(event.title()) if event.title() else ""
        start = str(fmt.stringFromDate_(event.startDate()))
        end = str(fmt.stringFromDate_(event.endDate()))
        location = str(event.location()) if event.location() else ""

        entry = f"[{cal_name}] {title}: {start} - {end}"
        if location:
            entry += f" @ {location}"
        lines.append(entry)

    return f"Today's calendar events ({len(lines)}):\n" + "\n".join(lines)

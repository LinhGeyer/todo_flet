import flet as ft
from datetime import datetime, timedelta
import json
import os
import calendar

# Define light and dark themes
LIGHT_THEME = ft.Theme(color_scheme_seed="blue")
DARK_THEME = ft.Theme(color_scheme_seed="blue")

# Function to create the AppBar
def create_appbar(page, toggle_theme, theme_mode):
    return ft.AppBar(
        title=ft.Text("To-Do List & Planner"),
        actions=[
            ft.IconButton(
                icon=ft.icons.BRIGHTNESS_6,
                tooltip="Toggle Theme",
                on_click=toggle_theme,
            ),
        ],
        bgcolor="white" if theme_mode == "light" else "black",
    )

# Datenstrukturen und Persistenz
todos = []
categories = ["School", "Personal", "Cleaning"]
DATA_FILE = "todos.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        todos = data.get("todos", [])
        categories = data.get("categories", categories)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({"todos": todos, "categories": categories}, f)

# Homepage
def homepage(page):
    def update_todo_list(sort_by="time", filter_by="all"):
        # Remove filtering by today's date to show all tasks
        all_todos = todos

        # Filter tasks based on the selected filter
        if filter_by == "done":
            filtered_todos = [todo for todo in all_todos if todo["done"]]
        elif filter_by == "todo":
            filtered_todos = [todo for todo in all_todos if not todo["done"]]
        else:
            filtered_todos = all_todos  # Show all tasks

        # Sorting
        if sort_by == "time":
            filtered_todos.sort(key=lambda x: x["time"])
        elif sort_by == "name":
            filtered_todos.sort(key=lambda x: x["name"])  # Corrected lambda syntax
        elif sort_by == "category":
            filtered_todos.sort(key=lambda x: x["category"])

        # Clear existing lists
        todo_list.controls.clear()

        # Add To-Do's to the list
        for todo in filtered_todos:
            todo_list.controls.append(
                ft.ListTile(
                    title=ft.Text(
                        todo["name"],
                        style=ft.TextStyle(
                            decoration=ft.TextDecoration.LINE_THROUGH if todo["done"] else None
                        )
                    ),
                    subtitle=ft.Text(f"Category: {todo['category']}, Time: {todo['time']}"),
                    leading=ft.Checkbox(value=todo["done"], on_change=lambda e: toggle_done(todo)),
                    trailing=ft.IconButton(  # Add delete button
                        icon=ft.icons.DELETE,
                        icon_color="red",
                        tooltip="Delete Task",
                        on_click=lambda e, t=todo: delete_task(t),
                    ),
                )
            )

        page.update()

    def toggle_done(todo):
        todo["done"] = not todo["done"]
        save_data()
        update_todo_list(sort_by=sort_radio.value, filter_by=filter_radio.value)

    def delete_task(todo):
        todos.remove(todo)  # Remove the task from the list
        save_data()
        update_todo_list(sort_by=sort_radio.value, filter_by=filter_radio.value)

    def change_sort(e):
        update_todo_list(sort_by=sort_radio.value, filter_by=filter_radio.value)

    def change_filter(e):
        update_todo_list(sort_by=sort_radio.value, filter_by=filter_radio.value)

    def toggle_settings(e):
        settings_menu.open = not settings_menu.open
        page.update()

    # UI Elements
    todo_list = ft.Column()

    # Sort and filter options
    sort_radio = ft.RadioGroup(
        value="time",  # Default sort by time
        content=ft.Column([
            ft.Radio(value="time", label="Sort by Time"),
            ft.Radio(value="name", label="Sort by Name"),
            ft.Radio(value="category", label="Sort by Category"),
        ]),
        on_change=change_sort,
    )

    filter_radio = ft.RadioGroup(
        value="all",  # Default filter by all
        content=ft.Column([
            ft.Radio(value="all", label="Show All"),
            ft.Radio(value="done", label="Show Done"),
            ft.Radio(value="todo", label="Show To-Do"),
        ]),
        on_change=change_filter,
    )

    # Settings menu
    settings_menu = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(
                content=ft.Column([
                    ft.Text("Sort by:", size=16, weight="bold"),
                    sort_radio,
                    ft.Text("Filter by:", size=16, weight="bold"),
                    filter_radio,
                ]),
            ),
        ],
    )

    # Initial load of tasks
    update_todo_list()

    return ft.Container(
        expand=True,  # Allow the container to expand and enable scrolling
        content=ft.Column(
            scroll="auto",  # Enable scrolling
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Today's To-Do's", size=20, weight="bold", expand=True),
                        settings_menu,  # Button for settings menu
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                todo_list,
                ft.ElevatedButton("Add To-Do", on_click=lambda _: page.go("/add_todo")),
                ft.ElevatedButton("Calendar", on_click=lambda _: page.go("/calendar")),
                ft.ElevatedButton("Manage Categories", on_click=lambda _: page.go("/categories")),
            ]
        )
    )

# Add To-Do Page
def add_todo_page(page):
    def add_todo(e):
        todos.append({
            "name": name_input.value,
            "date": date_input.value,  # Use the value from the date input field
            "time": time_input.value,  # Use the value from the time input field
            "category": category_dropdown.value,
            "location": location_input.value,
            "done": done_checkbox.value,
        })
        save_data()
        page.go("/")  # Return to homepage

    # UI Elements
    name_input = ft.TextField(label="To-Do Name", width=300)
    date_input = ft.TextField(label="Date (YYYY-MM-DD)", width=300, hint_text="e.g., 2023-10-01")
    time_input = ft.TextField(label="Time (HH:MM)", width=300, hint_text="e.g., 14:30")
    category_dropdown = ft.Dropdown(label="Category", options=[ft.dropdown.Option(c) for c in categories], width=300)
    location_input = ft.TextField(label="Location", width=300)
    done_checkbox = ft.Checkbox(label="Done", value=False)

    return ft.Container(
        expand=True,  # Allow the container to expand and enable scrolling
        content=ft.Column(
            scroll="auto",  # Enable scrolling
            controls=[
                ft.Text("Add a To-Do", size=20, weight="bold"),
                name_input,
                date_input,  # Replace DatePicker with a simple text field
                time_input,  # Replace TimePicker with a simple text field
                category_dropdown,
                location_input,
                done_checkbox,
                ft.ElevatedButton("Add To-Do", on_click=add_todo),
                ft.ElevatedButton("Back to Home", on_click=lambda _: page.go("/")),
            ]
        )
    )

# Calendar Page
def calendar_page(page):
    current_year = datetime.now().year
    current_month = datetime.now().month

    def change_month(e, delta):
        nonlocal current_year, current_month
        current_month += delta
        if current_month > 12:
            current_month = 1
            current_year += 1
        elif current_month < 1:
            current_month = 12
            current_year -= 1
        build_calendar(current_year, current_month)

    def change_year(e):
        nonlocal current_year
        current_year = int(year_picker.value)
        build_calendar(current_year, current_month)

    def change_month_dropdown(e):
        nonlocal current_month
        current_month = int(month_picker.value)
        build_calendar(current_year, current_month)

    def build_calendar(year=None, month=None):
        nonlocal current_year, current_month
        if year and month:
            current_year = year
            current_month = month

        # Get the calendar for the specified month and year
        month_cal = calendar.monthcalendar(current_year, current_month)

        # Clear the calendar grid
        calendar_grid.controls.clear()

        # Build the calendar grid
        for week in month_cal:
            for day in week:
                if (day == 0):
                    # Empty cell for days outside the month
                    calendar_grid.controls.append(ft.Container())
                else:
                    # Get tasks for this date
                    date_str = f"{current_year}-{current_month:02d}-{day:02d}"
                    tasks_for_day = [todo for todo in todos if todo["date"] == date_str]

                    # Build day cell with tasks
                    day_cell = ft.Container(
                        content=ft.Column([
                            ft.Text(day, size=16),
                            ft.Column(
                                controls=[ft.Text(todo["name"]) for todo in tasks_for_day],
                                spacing=2,
                            ),
                        ], spacing=5),
                        padding=10,
                        border=ft.border.all(1),
                        border_radius=5,
                        on_click=lambda e, date=date_str: show_day_tasks(date),
                    )
                    calendar_grid.controls.append(day_cell)

        page.update()

    def show_day_tasks(date):
        tasks_for_day = [todo for todo in todos if todo["date"] == date]

        # Clear the day tasks view
        day_tasks_view.controls.clear()

        # Add tasks to the day tasks view
        for todo in tasks_for_day:
            day_tasks_view.controls.append(
                ft.ListTile(
                    title=ft.Text(
                        todo["name"],
                        style=ft.TextStyle(
                            decoration=ft.TextDecoration.LINE_THROUGH if todo["done"] else None
                        )
                    ),
                    subtitle=ft.Text(f"Category: {todo['category']}, Time: {todo['time']}, Location: {todo['location']}"),
                    leading=ft.Checkbox(value=todo["done"], on_change=lambda e, t=todo: toggle_done(t)),
                )
            )

        # Show the day tasks view
        day_tasks_view.visible = True
        page.update()

    def toggle_done(todo):
        todo["done"] = not todo["done"]
        save_data()
        build_calendar()

    # UI Elements
    calendar_grid = ft.GridView(
        expand=1,
        runs_count=7,  # 7 days per week
        max_extent=100,  # Cell size
        spacing=5,
        run_spacing=5,
    )

    day_tasks_view = ft.Column(visible=False)

    # Initialize year_picker and month_picker
    year_picker = ft.Dropdown(
        options=[ft.dropdown.Option(str(y)) for y in range(2000, 2031)],
        value=str(current_year),
        width=100,
        on_change=change_year
    )

    month_picker = ft.Dropdown(
        options=[ft.dropdown.Option(str(m), text=calendar.month_name[m]) for m in range(1, 13)],
        value=str(current_month),
        width=120,
        on_change=change_month_dropdown
    )

    # Initial build
    build_calendar()

    return ft.Container(
        expand=True,  # Allow the container to expand and enable scrolling
        content=ft.Column(
            scroll="auto",  # Enable scrolling
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.NAVIGATE_BEFORE,
                            on_click=lambda e: change_month(e, -1)
                        ),
                        month_picker,  # Use the initialized month_picker
                        year_picker,   # Use the initialized year_picker
                        ft.IconButton(
                            icon=ft.icons.NAVIGATE_NEXT,
                            on_click=lambda e: change_month(e, 1)
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                calendar_grid,
                day_tasks_view,
                ft.ElevatedButton("Back to Home", on_click=lambda _: page.go("/")),
            ]
        )
    )

# Category Management Page
def categories_page(page):
    def add_category(e):
        if category_input.value.strip():  # Überprüfen, ob die Eingabe nicht leer ist
            categories.append(category_input.value.strip())
            categories.sort()  # Kategorien alphabetisch sortieren
            category_input.value = ""  # Eingabefeld leeren
            save_data()
            update_category_list()  # Kategorieliste aktualisieren

    def delete_category(category):
        categories.remove(category)  # Kategorie aus der Liste entfernen
        save_data()
        update_category_list()  # Kategorieliste aktualisieren

    def update_category_list():
        category_list.controls.clear()  # Vorherige Einträge löschen
        for category in categories:
            category_list.controls.append(
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            icon_color="red",
                            on_click=lambda e, cat=category: delete_category(cat),  # Löschbutton für die Kategorie
                        ),
                        ft.Text(category),  # Kategoriename anzeigen
                    ],
                    alignment=ft.MainAxisAlignment.START,
                )
            )
        page.update()

    # UI Elements
    category_input = ft.TextField(label="New Category", width=300)
    category_list = ft.Column()  # Liste zur Anzeige der Kategorien

    # Initiale Anzeige der Kategorien
    update_category_list()

    return ft.Container(
        expand=True,  # Allow the container to expand and enable scrolling
        content=ft.Column(
            scroll="auto",  # Enable scrolling
            controls=[
                ft.Text("Manage Categories", size=20, weight="bold"),
                category_input,
                ft.ElevatedButton("Add Category", on_click=add_category),
                ft.Text("Categories:", size=16, weight="bold"),
                category_list,  # List of categories
                ft.ElevatedButton("Back to Home", on_click=lambda _: page.go("/")),
            ]
        )
    )

# Main App
def main(page: ft.Page):
    page.title = "To-Do List & Planner"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = LIGHT_THEME
    page.dark_theme = DARK_THEME
    page.padding = 20

    # Function to toggle theme
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.appbar = create_appbar(page, toggle_theme, page.theme_mode)  # Update AppBar
        page.update()

    # AppBar
    page.appbar = create_appbar(page, toggle_theme, page.theme_mode)

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(ft.View("/", [homepage(page)]))
        elif page.route == "/add_todo":
            page.views.append(ft.View("/add_todo", [add_todo_page(page)]))
        elif page.route == "/calendar":
            page.views.append(ft.View("/calendar", [calendar_page(page)]))
        elif page.route == "/categories":
            page.views.append(ft.View("/categories", [categories_page(page)]))
        page.update()

    page.on_route_change = route_change
    page.go("/")

ft.app(target=main)

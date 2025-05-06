import tkinter as tk
from tkinter import messagebox, colorchooser

class TodoList:
    def __init__(self, root):
        self.root = root
        self.root.title("Todo List")
        self.tasks = []

        # GUI components
        self.task_entry = tk.Entry(self.root, width=50, bg="white", fg="black", font=("Arial", 12))
        self.task_entry.grid(row=0, column=0, padx=5, pady=5)

        self.add_button = tk.Button(self.root, text="Add Task", command=self.add_task, bg="pink", fg="black", font=("Arial", 12))
        self.add_button.grid(row=0, column=1, padx=5, pady=5)

        self.task_list = tk.Listbox(self.root, width=50, bg="white", fg="black", font=("Arial", 12), selectmode="extended")
        self.task_list.grid(row=1, column=0, padx=5, pady=5)

        self.delete_button = tk.Button(self.root, text="Delete Task", command=self.delete_task, bg="red", fg="black", font=("Arial", 12))
        self.delete_button.grid(row=1, column=1, padx=5, pady=5)

        self.update_button = tk.Button(self.root, text="Update Task", command=self.update_task, bg="yellow", fg="black", font=("Arial", 12))
        self.update_button.grid(row=2, column=1, padx=5, pady=5)

        self.clear_button = tk.Button(self.root, text="Clear All", command=self.clear_all, bg="orange", fg="black", font=("Arial", 12))
        self.clear_button.grid(row=2, column=0, padx=5, pady=5)

        self.color_button = tk.Button(self.root, text="Change Color", command=self.change_color, bg="purple", fg="black", font=("Arial", 12))
        self.color_button.grid(row=3, column=0, padx=5, pady=5)
        
        self.count_label = tk.Label(self.root, text="Total Tasks: 0", font=("Arial", 12), bg="#f0f0f0", fg="black")
        self.count_label.grid(row=4, column=0, columnspan=2, pady=5)

    def add_task(self):
        task = self.task_entry.get()
        if task:
            self.tasks.append(task)
            self.task_list.insert(tk.END, task)
            self.task_entry.delete(0, tk.END)
            self.update_count()

    def delete_task(self):
        selected_Tasks = self.task_list.curselection()  # Get selected indices
        if selected_Tasks:
            confirmation = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected_Tasks)} tasks?")
            if confirmation:
                for i in reversed(selected_Tasks):  # Reverse order to avoid index shifting errors
                    self.tasks.pop(i)
                    self.task_list.delete(i)
        else:
            messagebox.showwarning("Error", "Select one or more tasks to delete")
        self.update_count()

    def update_task(self):
        try:
            task_index = self.task_list.curselection()[0]
            new_task = self.task_entry.get()
            if new_task:
                self.tasks[task_index] = new_task
                self.update_task_list()
                self.task_entry.delete(0, tk.END)
        except IndexError:
            messagebox.showwarning("Error", "Select a task to update")

    def clear_all(self):
        self.tasks = []
        self.task_list.delete(0, tk.END)

    def change_color(self):
        colour = colorchooser.askcolor()[1]
        if colour:
            self.root.config(bg=colour)
            self.task_entry.config(bg=colour)
            self.task_list.config(bg=colour)

    def update_task_list(self):
        self.task_list.delete(0, tk.END)
        for task in self.tasks:
            self.task_list.insert(tk.END, task)
    
    def update_count(self):
        self.count_label.config(text=f"Total Tasks: {len(self.tasks)}")

def main():
    root = tk.Tk()
    todo = TodoList(root)
    root.mainloop()

if __name__ == "__main__":
    main()
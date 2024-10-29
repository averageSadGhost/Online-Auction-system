import tkinter as tk
from tkinter import messagebox
from auth import register_user, login_user

class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auth App")
        self.current_frame = None  # Track the current frame

        # Show the login screen by default
        self.show_login()

    def clear_frame(self):
        """Clear the current frame."""
        if self.current_frame is not None:
            self.current_frame.destroy()

    def show_login(self):
        """Display the login screen."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=20)

        tk.Label(self.current_frame, text="Login", font=("Arial", 20)).pack(pady=10)

        tk.Label(self.current_frame, text="Email").pack()
        email_entry = tk.Entry(self.current_frame)
        email_entry.pack()

        tk.Label(self.current_frame, text="Password").pack()
        password_entry = tk.Entry(self.current_frame, show="*")
        password_entry.pack()

        def handle_login():
            email = email_entry.get()
            password = password_entry.get()
            response, status = login_user(email, password)

            if status == 200:
                messagebox.showinfo("Success", "Login successful!")
            elif status == 403:
                messagebox.showwarning("Warning", response.get("detail", "Account not verified."))
            else:
                messagebox.showerror("Error", response.get("detail", "Invalid credentials."))

        tk.Button(self.current_frame, text="Login", command=handle_login).pack(pady=10)
        tk.Button(self.current_frame, text="Don't have an account? Register", 
                  command=self.show_register).pack(pady=10)

    def show_register(self):
        """Display the register screen."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=20)

        tk.Label(self.current_frame, text="Register", font=("Arial", 20)).pack(pady=10)

        tk.Label(self.current_frame, text="Email").pack()
        email_entry = tk.Entry(self.current_frame)
        email_entry.pack()

        tk.Label(self.current_frame, text="First Name").pack()
        first_name_entry = tk.Entry(self.current_frame)
        first_name_entry.pack()

        tk.Label(self.current_frame, text="Last Name").pack()
        last_name_entry = tk.Entry(self.current_frame)
        last_name_entry.pack()

        tk.Label(self.current_frame, text="Password").pack()
        password_entry = tk.Entry(self.current_frame, show="*")
        password_entry.pack()

        def handle_register():
            email = email_entry.get()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            password = password_entry.get()

            response, status = register_user(email, first_name, last_name, password)

            if status == 201:
                messagebox.showinfo("Success", "Registration successful! Please check your email for OTP.")
                self.show_login()  # Go back to login after successful registration
            else:
                messagebox.showerror("Error", str(response))

        tk.Button(self.current_frame, text="Register", command=handle_register).pack(pady=10)
        tk.Button(self.current_frame, text="Already have an account? Login", 
                  command=self.show_login).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthApp(root)
    root.mainloop()

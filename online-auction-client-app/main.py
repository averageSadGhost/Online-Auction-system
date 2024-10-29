import tkinter as tk
from tkinter import messagebox
import requests
from auth import register_user, login_user, resend_otp, verify_otp
import threading

class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auth App")
        self.current_frame = None
        self.user_email = None  # Store email for OTP verification
        self.timer_seconds = 180  # 3 minutes in seconds

        # Define buttons as instance variables
        self.login_button = None
        self.register_button = None

        # Show login screen by default
        self.show_login()

    def clear_frame(self):
        """Clear the current frame."""
        if self.current_frame is not None:
            self.current_frame.destroy()

    def set_button_loading(self, button):
        """Set the button to loading state."""
        button.config(text="Loading...", state='disabled')

    def reset_button(self, button, text):
        """Reset the button to its original state."""
        button.config(text=text, state='normal')

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
            self.set_button_loading(self.login_button)  # Set loading state on button

            email = email_entry.get()
            password = password_entry.get()

            # Start a thread for the login process
            threading.Thread(target=self.login_thread, args=(email, password)).start()

        self.login_button = tk.Button(self.current_frame, text="Login", command=handle_login)
        self.login_button.pack(pady=10)

        tk.Button(self.current_frame, text="Don't have an account? Register",
                  command=self.show_register).pack(pady=10)

    def login_thread(self, email, password):
        """Thread for logging in."""
        response, status = login_user(email, password)

        self.root.after(0, lambda: self.reset_button(self.login_button, "Login"))  # Reset button on the main thread

        if status == 200:
            self.root.after(0, lambda: messagebox.showinfo("Success", "Login successful!"))
        elif status == 403:
            self.root.after(0, lambda: messagebox.showwarning("Warning", response.get("detail", "Account not verified.")))
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", response.get("detail", "Invalid credentials.")))

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
            self.set_button_loading(self.register_button)  # Set loading state on button

            email = email_entry.get()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            password = password_entry.get()

            # Start a thread for the registration process
            threading.Thread(target=self.register_thread, args=(email, first_name, last_name, password)).start()

        self.register_button = tk.Button(self.current_frame, text="Register", command=handle_register)
        self.register_button.pack(pady=10)

        tk.Button(self.current_frame, text="Already have an account? Login",
                  command=self.show_login).pack(pady=10)

    def register_thread(self, email, first_name, last_name, password):
        """Thread for registering."""
        response, status = register_user(email, first_name, last_name, password)

        self.root.after(0, lambda: self.reset_button(self.register_button, "Register"))  # Reset button on the main thread

        if status == 201:
            self.root.after(0, lambda: messagebox.showinfo("Success", "Registration successful! Please check your email for OTP."))
            self.user_email = email  # Store email for OTP verification
            self.root.after(0, self.show_otp_screen)  # Go to OTP screen
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", str(response)))

    def show_otp_screen(self):
        """Display the OTP verification screen."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=20)

        tk.Label(self.current_frame, text="Verify OTP", font=("Arial", 20)).pack(pady=10)

        tk.Label(self.current_frame, text="Enter OTP").pack()
        otp_entry = tk.Entry(self.current_frame)
        otp_entry.pack()

        timer_label = tk.Label(self.current_frame, text="")
        timer_label.pack()

        self.resend_button = tk.Button(self.current_frame, text="Resend OTP", state="disabled", command=self.resend_otp)
        self.resend_button.pack(pady=10)

        def handle_otp_verification():
            self.set_button_loading(verify_button)  # Set loading state on button
            otp = otp_entry.get()
            response, status = verify_otp(self.user_email, otp)
            self.root.after(0, lambda: self.reset_button(verify_button, "Verify"))  # Reset button on the main thread

            if status == 200:
                self.root.after(0, lambda: messagebox.showinfo("Success", "Account verified successfully! Please log in."))
                self.show_login()  # Redirect to login
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", response.get("detail", "Invalid or expired OTP.")))

        verify_button = tk.Button(self.current_frame, text="Verify", command=handle_otp_verification)
        verify_button.pack(pady=10)

        # Start the 3-minute countdown timer
        self.start_timer(timer_label)

    def start_timer(self, label):
        """Start a countdown timer and enable the button when it reaches 0."""
        def countdown():
            minutes, seconds = divmod(self.timer_seconds, 60)
            label.config(text=f"Resend OTP in {minutes:02}:{seconds:02}")

            if self.timer_seconds > 0:
                self.timer_seconds -= 1
                # Call this function again after 1 second
                self.root.after(1000, countdown)
            else:
                # Enable the resend button when timer reaches 0
                self.resend_button.config(state="normal")

        countdown()

    def resend_otp(self):
        """Handle resending the OTP using the new endpoint."""
        self.set_button_loading(self.resend_button)  # Set loading state on button
        response, status = resend_otp(self.user_email)

        if status == 200:
            messagebox.showinfo("Success", "A new OTP has been sent to your email.")
            self.timer_seconds = 180  # Reset the timer to 3 minutes
            self.start_timer(tk.Label(self.current_frame))  # Restart the timer
        elif status == 400:
            messagebox.showwarning("Warning", response.get("detail", "OTP still valid."))
        elif status == 404:
            messagebox.showerror("Error", "User not found.")
        else:
            messagebox.showerror("Error", "Failed to resend OTP.")

        self.root.after(0, lambda: self.reset_button(self.resend_button, "Resend OTP"))  # Reset button after request

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthApp(root)
    root.mainloop()

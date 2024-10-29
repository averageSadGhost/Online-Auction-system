import tkinter as tk
from tkinter import messagebox
import requests
from auth import register_user, login_user, resend_otp, verify_otp

class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auth App")
        self.current_frame = None
        self.user_email = None  # Store email for OTP verification
        self.timer_seconds = 180  # 3 minutes in seconds

        # Show login screen by default
        self.show_login()

    def clear_frame(self):
        """Clear the current frame."""
        if self.current_frame is not None:
            self.current_frame.destroy()

    def show_loading(self, text="Please wait..."):
        """Display a loading indicator in place of a button."""
        self.loading_label = tk.Label(self.current_frame, text=text, font=("Arial", 16))
        self.loading_label.pack(pady=20)
        self.loading_label.update()  # Refresh to show loading text immediately

    def hide_loading(self):
        """Remove the loading indicator."""
        self.loading_label.destroy()

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
            self.show_loading()  # Show loading indicator
            email = email_entry.get()
            password = password_entry.get()

            response, status = login_user(email, password)
            self.hide_loading()  # Hide loading indicator

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
            self.show_loading("Registering...")  # Show loading indicator
            email = email_entry.get()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            password = password_entry.get()

            response, status = register_user(email, first_name, last_name, password)
            self.hide_loading()  # Hide loading indicator

            if status == 201:
                messagebox.showinfo("Success", "Registration successful! Please check your email for OTP.")
                self.user_email = email  # Store email for OTP verification
                self.show_otp_screen()  # Go to OTP screen
            else:
                messagebox.showerror("Error", str(response))

        tk.Button(self.current_frame, text="Register", command=handle_register).pack(pady=10)
        tk.Button(self.current_frame, text="Already have an account? Login",
                  command=self.show_login).pack(pady=10)

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
            self.show_loading("Verifying OTP...")  # Show loading indicator
            otp = otp_entry.get()
            response, status = verify_otp(self.user_email, otp)
            self.hide_loading()  # Hide loading indicator

            if status == 200:
                messagebox.showinfo("Success", "Account verified successfully! Please log in.")
                self.show_login()  # Redirect to login
            else:
                messagebox.showerror("Error", response.get("detail", "Invalid or expired OTP."))

        tk.Button(self.current_frame, text="Verify", command=handle_otp_verification).pack(pady=10)

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
        self.show_loading("Sending OTP...")  # Show loading indicator
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

        self.hide_loading()  # Hide loading indicator after request is done

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthApp(root)
    root.mainloop()

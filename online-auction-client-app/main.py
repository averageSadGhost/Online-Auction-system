import tkinter as tk
from tkinter import messagebox
import requests
import threading
import json
from auction import get_auctions
from auth import login_user, register_user, resend_otp, verify_otp
from utils import load_token  # Assuming load_token function is defined in utils to load the token


class AuctionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auction App")
        self.current_frame = None
        self.user_email = None  # Store email for OTP verification
        self.timer_seconds = 180  # 3 minutes in seconds

        # Define buttons as instance variables
        self.login_button = None
        self.register_button = None

        # Check if token is stored and valid, then either show auctions or login screen
        if self.is_token_valid():
            self.show_navbar()  # Go directly to the auction screen
        else:
            self.show_login()  # Show login screen

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
            self.root.after(0, self.show_navbar)  # Show navigation bar after login
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

    def show_navbar(self):
        """Display the navigation bar after login."""
        self.clear_frame()
        navbar = tk.Frame(self.root, bg="lightgray")
        navbar.pack(side="top", fill="x")

        tk.Button(navbar, text="Available Auctions", command=self.show_available_auctions).pack(side="left", padx=10, pady=5)
        tk.Button(navbar, text="My Auctions", command=self.show_my_auctions).pack(side="left", padx=10, pady=5)

        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=20)

        # Show available auctions by default
        self.show_available_auctions()

    def show_available_auctions(self):
        """Display available auctions."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=20)

        tk.Label(self.current_frame, text="Available Auctions", font=("Arial", 20)).pack(pady=10)

        # Fetch auctions in a separate thread to avoid blocking the UI
        def fetch_and_display_auctions():
            auctions, status = get_auctions()
            if status == 200:
                # Display the fetched auctions
                if auctions:
                    for auction in auctions:
                        tk.Label(self.current_frame, text=auction.get("title", "Untitled Auction")).pack()
                else:
                    tk.Label(self.current_frame, text="No auctions available.").pack()
            else:
                tk.Label(self.current_frame, text="Failed to fetch auctions. Please try again.").pack()

        threading.Thread(target=fetch_and_display_auctions).start()

    def show_my_auctions(self):
        """Display my auctions."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=20)

        tk.Label(self.current_frame, text="My Auctions", font=("Arial", 20)).pack(pady=10)

        # Placeholder for user's auctions
        tk.Label(self.current_frame, text="No auctions available.").pack()

    def is_token_valid(self):
        """Check if the token is valid by trying to fetch auctions."""
        token = load_token()  # Load the token from local storage
        if token:
            response, status = get_auctions()
            if status == 200:
                return True
        return False


if __name__ == "__main__":
    root = tk.Tk()
    app = AuctionApp(root)
    root.mainloop()

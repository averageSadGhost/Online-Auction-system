import tkinter as tk
from tkinter import messagebox
import threading
from datetime import datetime 
from auction import get_auction_details, get_auctions, get_my_auctions, join_auction
from auth import get_logged_in_user_details, login_user, register_user, resend_otp, verify_otp
from utils import calculate_hours_until, delete_token, load_token
from PIL import Image, ImageTk
from io import BytesIO
import requests



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
        self.clear_frame()  # Clear any existing frames
        
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=20)

        tk.Label(self.current_frame, text="Login", font=("Arial", 20)).pack(pady=10)

        # Email entry field
        tk.Label(self.current_frame, text="Email").pack()
        email_entry = tk.Entry(self.current_frame)
        email_entry.pack()

        # Password entry field
        tk.Label(self.current_frame, text="Password").pack()
        password_entry = tk.Entry(self.current_frame, show="*")
        password_entry.pack()

        def handle_login():
            self.set_button_loading(self.login_button)  # Set loading state on button
            
            email = email_entry.get()
            password = password_entry.get()

            # Start a thread for the login process
            threading.Thread(target=self.login_thread, args=(email, password)).start()

        # Login button
        self.login_button = tk.Button(self.current_frame, text="Login", command=handle_login)
        self.login_button.pack(pady=10)

        # Register button
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
            
    def show_otp_screen(self):
        """Display the OTP verification screen."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=20)

        tk.Label(self.current_frame, text="OTP Verification", font=("Arial", 20)).pack(pady=10)
        tk.Label(self.current_frame, text=f"Please enter the OTP sent to {self.user_email}", wraplength=300).pack()

        # OTP entry field
        otp_entry = tk.Entry(self.current_frame, font=("Arial", 14), justify='center', width=6)
        otp_entry.pack(pady=20)

        # Timer label with better visibility
        timer_label = tk.Label(
            self.current_frame,
            text="",
            font=("Arial", 12),
            fg="blue"
        )
        timer_label.pack(pady=10)

        # Buttons frame
        buttons_frame = tk.Frame(self.current_frame)
        buttons_frame.pack(pady=10)

        verify_button = tk.Button(buttons_frame, text="Verify OTP", width=15)
        verify_button.pack(side=tk.LEFT, padx=5)

        resend_button = tk.Button(buttons_frame, text="Resend OTP", width=15, state=tk.DISABLED)
        resend_button.pack(side=tk.LEFT, padx=5)

        def update_timer(remaining):
            """Update the timer display."""
            if remaining <= 0:
                timer_label.config(text="You can now resend the OTP", fg="green")
                resend_button.config(state=tk.NORMAL)
                return
            
            minutes = remaining // 60
            seconds = remaining % 60
            timer_label.config(
                text=f"Resend available in {minutes:02d}:{seconds:02d}",
                fg="blue"
            )
            self.root.after(1000, update_timer, remaining - 1)

        def handle_verify():
            """Handle OTP verification."""
            if not otp_entry.get().strip():
                messagebox.showwarning("Warning", "Please enter the OTP")
                return
                
            self.set_button_loading(verify_button)
            otp = otp_entry.get()
            
            threading.Thread(target=verify_otp_thread, args=(otp,)).start()

        def verify_otp_thread(otp):
            """Thread for OTP verification."""
            response, status = verify_otp(self.user_email, otp)
            
            self.root.after(0, lambda: self.reset_button(verify_button, "Verify OTP"))

            if status == 200:
                self.root.after(0, lambda: messagebox.showinfo("Success", "Email verified successfully!"))
                self.root.after(0, self.show_login)
            else:
                error_msg = response.get("detail", "Invalid OTP. Please try again.")
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))

        def handle_resend():
            """Handle OTP resend."""
            self.set_button_loading(resend_button)
            threading.Thread(target=resend_otp_thread).start()

        def resend_otp_thread():
            """Thread for resending OTP."""
            response, status = resend_otp(self.user_email)
            
            self.root.after(0, lambda: self.reset_button(resend_button, "Resend OTP"))

            if status == 200:
                self.root.after(0, lambda: messagebox.showinfo("Success", "OTP resent successfully!"))
                resend_button.config(state=tk.DISABLED)
                timer_label.config(fg="blue")
                update_timer(self.timer_seconds)
            else:
                error_msg = response.get("detail", "Failed to resend OTP. Please try again.")
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))

        # Configure button commands
        verify_button.config(command=handle_verify)
        resend_button.config(command=handle_resend)

        # Start the initial timer
        update_timer(self.timer_seconds)

        # Add a back to login button
        tk.Button(
            self.current_frame,
            text="Back to Login",
            command=self.show_login
        ).pack(pady=20)

    def show_navbar(self):
        """Display the navigation bar after login."""
        # Ensure that the current frame is cleared before showing the navbar
        self.clear_frame()

        if hasattr(self, 'navbar') and self.navbar is not None:
            self.navbar.destroy()  # Destroy the navbar if it's already shown
        
        self.navbar = tk.Frame(self.root, bg="lightgray")
        self.navbar.pack(side="top", fill="x")

        tk.Button(self.navbar, text="Available Auctions", command=self.show_available_auctions).pack(side="left", padx=10, pady=5)
        tk.Button(self.navbar, text="My Auctions", command=self.show_my_auctions).pack(side="left", padx=10, pady=5)
        tk.Button(self.navbar, text="Profile", command=self.show_profile).pack(side="left", padx=10, pady=5)  # Profile button

        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=20)

        # Show available auctions by default
        self.show_available_auctions()

    def show_profile(self):
        """Display the profile of the logged-in user."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=20)

        tk.Label(self.current_frame, text="Profile", font=("Arial", 20)).pack(pady=10)

        def fetch_profile():
            user_details, status = get_logged_in_user_details()  # Call the profile API function
            if status == 200:
                name = f"{user_details.get('first_name', '')} {user_details.get('last_name', '')}"
                email = user_details.get('email', 'Unknown email')

                tk.Label(self.current_frame, text=f"Name: {name}", font=("Arial", 14)).pack(pady=10)
                tk.Label(self.current_frame, text=f"Email: {email}", font=("Arial", 14)).pack(pady=10)
            else:
                tk.Label(self.current_frame, text="Failed to fetch profile details. Please try again.", font=("Arial", 12), fg="red").pack(pady=10)

            # Add a Logout button
            logout_button = tk.Button(
                self.current_frame,
                text="Logout",
                font=("Arial", 14),
                command=self.handle_logout  # Link to the logout handler
            )
            logout_button.pack(pady=20)

        threading.Thread(target=fetch_profile).start()  # Fetch user details in a separate thread

    def clear_frame(self):
        """Clear the current frame."""
        if self.current_frame is not None:
            self.current_frame.destroy()  # Destroy the current frame content

    def handle_logout(self):
        """Handle user logout."""
        if delete_token():  # Call the delete_token function
            messagebox.showinfo("Logged Out", "You have been logged out successfully.")
            
            self.clear_frame()  # Clear the content frame
            if hasattr(self, 'navbar'):
                self.navbar.destroy()  # Destroy the navbar if it exists
            
            self.show_login()  # Show the login screen after logout
        else:
            messagebox.showerror("Error", "Failed to logout. Please try again.")



    def show_available_auctions(self):
        """Display available auctions with a scrollable view."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)  # Reinitialize the frame
        self.current_frame.pack(pady=20, expand=True)

        title_frame = tk.Frame(self.current_frame)
        title_frame.pack(fill="x")

        tk.Label(title_frame, text="Available Auctions", font=("Arial", 20)).pack(pady=10)

        wrapper_frame = tk.Frame(self.current_frame)
        wrapper_frame.pack(expand=True, fill="both")

        canvas = tk.Canvas(wrapper_frame, height=400, width=250)
        scrollbar = tk.Scrollbar(wrapper_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        wrapper_frame.grid_rowconfigure(0, weight=1)
        wrapper_frame.grid_columnconfigure(0, weight=1)

        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")

        def fetch_and_display_auctions():
            auctions, status = get_auctions()
            if status == 200:
                if auctions:
                    for auction in auctions:
                        frame = tk.Frame(scrollable_frame, pady=10)
                        frame.pack()

                        image_url = auction.get("image")
                        try:
                            response = requests.get(image_url)
                            response.raise_for_status()
                            image_data = BytesIO(response.content)

                            pil_image = Image.open(image_data)
                            pil_image = pil_image.resize((200, 200))
                            tk_image = ImageTk.PhotoImage(pil_image)

                            img_label = tk.Label(frame, image=tk_image)
                            img_label.image = tk_image
                            img_label.pack()
                        except requests.RequestException:
                            tk.Label(frame, text="[Image not available]").pack()

                        # Create a title_frame for each auction
                        title_frame = tk.Frame(frame)
                        title_frame.pack(fill="x")

                        title = auction.get("title", "Untitled Auction")
                        start_time = auction.get("start_date_time")

                        # Title Label in the center (with columnspan to span the full width)
                        title_label = tk.Label(title_frame, text=title, font=("Arial", 14), wraplength=230, anchor="center")
                        title_label.grid(row=0, column=0, sticky="nsew", padx=25, pady=5)

                        # Time Label in the row below the title
                        time_left = calculate_hours_until(start_time)
                        time_text = ""
                        if time_left[0] == 0:
                            time_text = f"Starting in {time_left[1]} minutes"
                        elif time_left[1] == 0:
                            time_text = f"Starting in {time_left[0]} hours"
                        else:
                            time_text = f"Starting in {time_left[0]} hours {time_left[1]} minutes"

                        # Center the time label
                        time_label = tk.Label(
                            title_frame,
                            text=time_text,
                            font=("Arial", 12),
                            fg="gray",
                            anchor="center"
                        )
                        time_label.grid(row=1, column=0, padx=25, pady=5)

                        # Add a button under the title to view details
                        button_text = f"View auction details"
                        button = tk.Button(frame, text=button_text, command=lambda auction_id=auction["id"]: self.show_auction_details(auction_id))
                        button.pack(pady=10)

                else:
                    tk.Label(scrollable_frame, text="No auctions available.").pack()
            else:
                tk.Label(scrollable_frame, text="Failed to fetch auctions. Please try again.").pack()

        threading.Thread(target=fetch_and_display_auctions).start()







    def show_auction_details(self, auction_id):
        """Display the details of a specific auction."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=20)

        auction_details, status = get_auction_details(auction_id)
        if status == 200:
            title = auction_details.get("title", "Untitled Auction")
            description = auction_details.get("description", "No description available.")
            start_date_time = auction_details.get("start_date_time", "Not available")
            end_date_time = auction_details.get("end_date_time", "Not available")
            starting_price = auction_details.get("starting_price", "N/A")
            image_url = auction_details.get("image", "")
            is_participant = auction_details.get("is_participant", False)

            # Format the start_date_time and end_date_time to "year/month/day hour:minutes AM/PM"
            try:
                formated_start_date_time = datetime.strptime(start_date_time, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y/%m/%d %I:%M %p")
                formated_end_date_time = datetime.strptime(end_date_time, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y/%m/%d %I:%M %p")
            except ValueError:
                formated_start_date_time = "Invalid date format"
                formated_end_date_time = "Invalid date format"

            # Display auction title
            tk.Label(self.current_frame, text=title, font=("Arial", 20)).pack(pady=10)

            # Display auction image
            try:
                response = requests.get(image_url)
                response.raise_for_status()
                image_data = BytesIO(response.content)
                pil_image = Image.open(image_data)
                pil_image = pil_image.resize((400, 400))
                tk_image = ImageTk.PhotoImage(pil_image)
                img_label = tk.Label(self.current_frame, image=tk_image)
                img_label.image = tk_image
                img_label.pack()
            except requests.RequestException:
                tk.Label(self.current_frame, text="[Image not available]").pack()

            # Display auction description
            tk.Label(self.current_frame, text="Description:", font=("Arial", 14)).pack(pady=10)
            tk.Label(self.current_frame, text=description, font=("Arial", 12), wraplength=400).pack(pady=10)

            # Display starting price and start time
            tk.Label(self.current_frame, text=f"Starting Price: {starting_price}", font=("Arial", 14)).pack(pady=10)
            tk.Label(self.current_frame, text=f"Starts on: {formated_start_date_time}", font=("Arial", 14)).pack(pady=10)
            tk.Label(self.current_frame, text=f"Ends on: {formated_end_date_time}", font=("Arial", 14)).pack(pady=10)

            # Display participation status or join button
            if is_participant:
                tk.Label(
                    self.current_frame,
                    text="You are already a participant in this auction.",
                    font=("Arial", 14),
                    fg="green"
                ).pack(pady=20)
            else:
                join_button = tk.Button(
                    self.current_frame,
                    text="Join Auction",
                    font=("Arial", 14),
                    command=lambda: self.handle_join_auction(auction_id)
                )
                join_button.pack(pady=20)

        else:
            tk.Label(self.current_frame, text="Failed to fetch auction details. Please try again.").pack(pady=10)

    def handle_join_auction(self, auction_id):
        """Handle the action to join an auction."""
        response, status = join_auction(auction_id)  # Call the join_auction API function

        if status == 200:
            messagebox.showinfo("Success", "You have successfully joined the auction.")
            # Reload the auction details screen to reflect the new state
            self.show_auction_details(auction_id)
        elif status == 400:
            error_message = response.get("error", "Invalid request.")
            messagebox.showerror("Error", error_message)
        elif status == 404:
            messagebox.showerror("Error", "Auction not found.")
        else:
            messagebox.showerror("Error", "Failed to join the auction. Please try again.")

    def show_my_auctions(self):
        """Display auctions that the user is participating in with a scrollable view."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)  # Reinitialize the frame
        self.current_frame.pack(pady=20, expand=True)

        title_frame = tk.Frame(self.current_frame)
        title_frame.pack(fill="x")

        tk.Label(title_frame, text="My Auctions", font=("Arial", 20)).pack(pady=10)

        wrapper_frame = tk.Frame(self.current_frame)
        wrapper_frame.pack(expand=True, fill="both")

        canvas = tk.Canvas(wrapper_frame, height=400, width=250)
        scrollbar = tk.Scrollbar(wrapper_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        wrapper_frame.grid_rowconfigure(0, weight=1)
        wrapper_frame.grid_columnconfigure(0, weight=1)

        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")

        # Fetch and display user's auctions
        def fetch_and_display_my_auctions():
            auctions, status = get_my_auctions()
            if status == 200:
                if auctions:
                    for auction in auctions:
                        frame = tk.Frame(scrollable_frame, pady=10)
                        frame.pack(fill="x")

                        title = auction.get("title", "Untitled Auction")
                        start_time = auction.get("start_date_time", "Not available")
                        starting_price = auction.get("starting_price", "N/A")
                        status_text = auction.get("status", "Unknown status")

                        # Format the start_date_time to "year/month/day hour:minutes AM/PM"
                        try:
                            formatted_date_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y/%m/%d %I:%M %p")
                        except ValueError:
                            formatted_date_time = "Invalid date format"

                        # Title and starting price frame
                        title_price_frame = tk.Frame(frame)
                        title_price_frame.pack(fill="x")

                        # Centered title
                        tk.Label(
                            title_price_frame, 
                            text=title, 
                            font=("Arial", 14, "bold"), 
                            wraplength=250, 
                            justify="center"
                        ).pack(anchor="center", pady=(0, 5))

                        # Centered starting price
                        tk.Label(
                            title_price_frame, 
                            text=f"Starting at {starting_price}", 
                            font=("Arial", 12),
                            justify="center"
                        ).pack(anchor="center", pady=(0, 10))

                        # Display the image
                        image_url = auction.get("image", "")
                        try:
                            response = requests.get(image_url)
                            response.raise_for_status()
                            image_data = BytesIO(response.content)
                            pil_image = Image.open(image_data)
                            pil_image = pil_image.resize((200, 200))
                            tk_image = ImageTk.PhotoImage(pil_image)

                            img_label = tk.Label(frame, image=tk_image)
                            img_label.image = tk_image
                            img_label.pack()
                        except requests.RequestException:
                            tk.Label(frame, text="[Image not available]").pack()

                        # Display the start date and status
                        tk.Label(
                            frame, 
                            text=f"Start Date: {formatted_date_time}", 
                            font=("Arial", 12)
                        ).pack()

                        tk.Label(
                            frame, 
                            text=f"Status: {status_text}", 
                            font=("Arial", 12), 
                            fg="gray"
                        ).pack(pady=5)

                        # View Auction button
                        button = tk.Button(
                            frame,
                            text="View Auction", 
                            command=lambda auction_id=auction["id"]: self.show_auction_details(auction_id)
                        )
                        button.pack(pady=10)

                else:
                    tk.Label(scrollable_frame, text="You have not joined any auctions yet.").pack()
            else:
                tk.Label(scrollable_frame, text="Failed to fetch your auctions. Please try again.").pack()

        threading.Thread(target=fetch_and_display_my_auctions).start()

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

import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
import uuid

# Path to CSV file
FILE_PATH = "patients.csv"

class Patient:
    """Class representing a patient."""
    def __init__(self, name, email, password, role, uid, conditions, prescriptions):
        self.__name = name
        self.__email = email
        self.__password = password
        self.role = role
        self.uid = uid
        self.conditions = conditions  # List of medical conditions
        self.prescriptions = prescriptions  # List of prescriptions

    def check_password(self, password):
        return self.__password == password

    def get_name(self):
        return self.__name

    def get_email(self):
        return self.__email

    def get_conditions(self):
        return self.conditions

    def get_prescriptions(self):
        return self.prescriptions

    def set_conditions(self, conditions):
        self.conditions = conditions

    def set_prescriptions(self, prescriptions):
        self.prescriptions = prescriptions

    def set_password(self, new_password):
        self.__password = new_password

    @staticmethod
    def from_dict(data):
        """Create a Patient instance from a dictionary."""
        return Patient(data['name'],
                       data['email'],
                       data['password'],
                       data['role'],
                       data['uid'],
                       data['conditions'].split(','),
                       data['prescriptions'].split(',')
                       )

    def to_dict(self):
        """Convert the Patient instance to a dictionary."""
        return {
            'name': self.__name,
            'email': self.__email,
            'password': self.__password,
            'role': self.role,
            'uid': self.uid,
            'conditions': ','.join(self.conditions),
            'prescriptions': ','.join(self.prescriptions)
        }


class Admin(Patient):
    """Admin class inheriting from Patient."""
    def __init__(self, name, email, password, uid, conditions, prescriptions):
        super().__init__(name, email, password, "admin", uid, conditions, prescriptions)


class HealthCareApp:
    """Main healthcare application."""
    def __init__(self):
        self.current_user = None
        self.__patients = []  # Private attribute for storing patient records
        self.setup_csv()
        self.load_patients()
        self.show_login_screen()

    def setup_csv(self):
        """Initialize the CSV file if it doesn't exist."""
        if not os.path.exists(FILE_PATH):
            with open(FILE_PATH, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    "name", "email", "password", "role", "uid", "conditions", "prescriptions"
                ])

    def load_patients(self):
        """Load patients from the CSV file."""
        with open(FILE_PATH, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                patient = Admin.from_dict(row) if row['role'] == 'admin' \
                    else Patient.from_dict(row)
                self.__patients.append(patient)

    def save_patients(self):
        """Save all patients to the CSV file."""
        with open(FILE_PATH, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=[
                "name", "email", "password", "role", "uid", "conditions", "prescriptions"
            ])
            writer.writeheader()
            for patient in self.__patients:
                writer.writerow(patient.to_dict())

    def find_patient(self, email):
        """Find a patient by email."""
        for patient in self.__patients:
            if patient.get_email() == email:
                return patient
        return None

    def add_patient(self, patient):
        """Add a new patient to the application."""
        self.__patients.append(patient)
        self.save_patients()

    def delete_patient(self, email):
        """Delete a patient from the system."""
        patient = self.find_patient(email)
        if patient:
            self.__patients.remove(patient)
            self.save_patients()
            return True
        return False

    def login(self, email, password):
        """Authenticate a patient based on email and password."""
        patient = self.find_patient(email)
        if patient and patient.check_password(password):
            return patient
        return None

    def show_login_screen(self):
        """Login window (check email, password)."""
        def handle_login():
            email = email_entry.get()
            password = password_entry.get()
            patient = self.login(email, password)
            if patient:
                self.current_user = patient
                login_window.destroy()
                if patient.role == 'admin':
                    self.show_admin_screen()
                else:
                    self.show_patient_screen()
            else:
                messagebox.showerror("Error", "Invalid email or password")

        def handle_register():
            login_window.destroy()
            self.show_register_screen()

        # Login interface
        login_window = tk.Tk()
        login_window.title("Login")
        login_window.geometry("600x400")

        login_frame = tk.Frame(login_window)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(login_window, text="Login", font=('Arial', 20)).pack(pady=50)
        tk.Label(login_frame, text="Email:", font=('Arial', 20)).grid(row=0, column=0, pady=5, padx=5)
        email_entry = tk.Entry(login_frame, font=('Arial', 20))
        email_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(login_frame, text="Password:", font=('Arial', 20)).grid(row=1, column=0, pady=5, padx=5)
        password_entry = tk.Entry(login_frame, show="*", font=('Arial', 20))
        password_entry.grid(row=1, column=1, pady=5, padx=5)

        tk.Button(login_frame, text="Login", command=handle_login, font=('Arial', 15)).grid(row=2, column=0, pady=5, padx=5)
        tk.Button(login_frame, text="Register", command=handle_register, font=('Arial', 15)).grid(row=2, column=1, pady=5, padx=5)

        login_window.mainloop()

    def show_register_screen(self):
        """Display the registration window."""
        def handle_register():
            name = name_entry.get()
            email = email_entry.get()
            password = password_entry.get()
            uid = str(uuid.uuid4())[:8]  # Generate UID
            conditions = conditions_entry.get().split(',')
            prescriptions = prescriptions_entry.get().split(',')

            if not (name and email and password and conditions_entry.get() and prescriptions_entry.get()):
                messagebox.showerror("Error", "Please complete the form!")
                return

            if self.find_patient(email):
                messagebox.showerror("Error", "Email is already registered!")
                return

            new_patient = Patient(name, email, password, "patient", uid, conditions, prescriptions)
            self.add_patient(new_patient)  # Add patient to the list
            messagebox.showinfo("Success", "Account registered successfully!")
            register_window.destroy()
            self.show_login_screen()

        # Register interface
        register_window = tk.Tk()
        register_window.title("Register")
        register_window.geometry("600x400")

        register_frame = tk.Frame(register_window)
        register_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(register_window, text="Register", font=('Arial', 20)).pack(pady=10)
        tk.Label(register_frame, text="Name:", font=('Arial', 20)).grid(row=0, column=0, pady=5, padx=5)
        name_entry = tk.Entry(register_frame, font=('Arial', 20))
        name_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(register_frame, text="Email:", font=('Arial', 20)).grid(row=1, column=0, pady=5, padx=5)
        email_entry = tk.Entry(register_frame, font=('Arial', 20))
        email_entry.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(register_frame, text="Password:", font=('Arial', 20)).grid(row=2, column=0, pady=5, padx=5)
        password_entry = tk.Entry(register_frame, show="*", font=('Arial', 20))
        password_entry.grid(row=2, column=1, pady=5, padx=5)

        tk.Label(register_frame, text="Conditions:", font=('Arial', 20)).grid(row=3, column=0, pady=5, padx=5)
        conditions_entry = tk.Entry(register_frame, font=('Arial', 20))
        conditions_entry.grid(row=3, column=1, pady=5, padx=5)

        tk.Label(register_frame, text="Prescriptions:", font=('Arial', 20)).grid(row=4, column=0, pady=5, padx=5)
        prescriptions_entry = tk.Entry(register_frame, font=('Arial', 20))
        prescriptions_entry.grid(row=4, column=1, pady=5, padx=5)

        tk.Button(register_frame, text="Register", command=handle_register, font=('Arial', 15)).grid(row=5, column=0, pady=5, padx=5)

        register_window.mainloop()

    def show_patient_screen(self):
        """Show the patient dashboard with an improved interface."""
        if self.current_user:
            screen = tk.Tk()
            screen.title("Patient Dashboard")
            screen.geometry("800x600")
            screen.configure(bg="#f0f0f0")

            header_frame = tk.Frame(screen, bg="#4CAF50")
            header_frame.pack(fill="x")

            tk.Label(header_frame, text="Patient Dashboard", font=('Arial', 24), bg="#4CAF50", fg="white").pack(pady=20)

            content_frame = tk.Frame(screen, bg="#f0f0f0")
            content_frame.pack(pady=20)

            tk.Label(content_frame, text="Conditions:", font=('Arial', 18), bg="#f0f0f0").grid(row=0, column=0, sticky="w", pady=10)
            conditions_text = tk.Text(content_frame, height=5, width=50, font=('Arial', 14))
            conditions_text.insert(tk.END, "\n".join(self.current_user.get_conditions()))
            conditions_text.config(state=tk.DISABLED)
            conditions_text.grid(row=1, column=0, pady=10)

            tk.Label(content_frame, text="Prescriptions:", font=('Arial', 18), bg="#f0f0f0").grid(row=2, column=0, sticky="w", pady=10)
            prescriptions_text = tk.Text(content_frame, height=5, width=50, font=('Arial', 14))
            prescriptions_text.insert(tk.END, "\n".join(self.current_user.get_prescriptions()))
            prescriptions_text.config(state=tk.DISABLED)
            prescriptions_text.grid(row=3, column=0, pady=10)

            button_frame = tk.Frame(screen, bg="#f0f0f0")
            button_frame.pack(pady=20)

            tk.Button(button_frame, text="Update Conditions", command=self.update_patient_conditions, font=('Arial', 15), bg="#4CAF50", fg="white").grid(row=0, column=0, padx=10, pady=10)
            tk.Button(button_frame, text="Update Prescriptions", command=self.update_patient_prescriptions, font=('Arial', 15), bg="#4CAF50", fg="white").grid(row=0, column=1, padx=10, pady=10)

            screen.mainloop()

    def update_patient_conditions(self):
        """Allow patients to update their conditions."""
        def save_conditions():
            new_conditions = conditions_entry.get().split(',')
            self.current_user.set_conditions(new_conditions)
            self.save_patients()
            update_window.destroy()

        update_window = tk.Tk()
        update_window.title("Update Conditions")

        tk.Label(update_window, text="New Conditions:", font=('Arial', 15)).pack(pady=10)
        conditions_entry = tk.Entry(update_window, font=('Arial', 15))
        conditions_entry.insert(0, ', '.join(self.current_user.get_conditions()))
        conditions_entry.pack(pady=10)

        tk.Button(update_window, text="Save", command=save_conditions, font=('Arial', 15)).pack(pady=10)

        update_window.mainloop()

    def update_patient_prescriptions(self):
        """Allow patients to update their prescriptions."""
        def save_prescriptions():
            new_prescriptions = prescriptions_entry.get().split(',')
            self.current_user.set_prescriptions(new_prescriptions)
            self.save_patients()
            update_window.destroy()

        update_window = tk.Tk()
        update_window.title("Update Prescriptions")

        tk.Label(update_window, text="New Prescriptions:", font=('Arial', 15)).pack(pady=10)
        prescriptions_entry = tk.Entry(update_window, font=('Arial', 15))
        prescriptions_entry.insert(0, ', '.join(self.current_user.get_prescriptions()))
        prescriptions_entry.pack(pady=10)

        tk.Button(update_window, text="Save", command=save_prescriptions, font=('Arial', 15)).pack(pady=10)

        update_window.mainloop()

    def show_admin_screen(self):
        """Show the admin dashboard."""
        admin_screen = tk.Tk()
        admin_screen.title("Admin Dashboard")

        tk.Label(admin_screen, text="Admin Dashboard", font=('Arial', 20)).pack(pady=10)

        # List patients
        tk.Label(admin_screen, text="All Patients:", font=('Arial', 15)).pack(pady=10)
        patient_list = ttk.Treeview(admin_screen, columns=("Name", "Email", "Conditions", "Prescriptions"), show="headings")
        patient_list.heading("Name", text="Name")
        patient_list.heading("Email", text="Email")
        patient_list.heading("Conditions", text="Conditions")
        patient_list.heading("Prescriptions", text="Prescriptions")

        for patient in self.__patients:
            patient_list.insert("", "end", values=(patient.get_name(), patient.get_email(),
                                                    "\n".join(patient.get_conditions()),
                                                    "\n".join(patient.get_prescriptions())))

        patient_list.pack(pady=10)

        # Admin functionalities
        def edit_conditions(email):
            patient = self.find_patient(email)
            if patient:
                self.update_patient_conditions_for_admin(patient)

        def edit_prescriptions(email):
            patient = self.find_patient(email)
            if patient:
                self.update_patient_prescriptions_for_admin(patient)

        def reset_password(email):
            patient = self.find_patient(email)
            if patient:
                self.reset_patient_password(patient)

        # Buttons to edit
        button_frame = tk.Frame(admin_screen)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Edit Conditions", command=lambda: edit_conditions(patient.get_email()), font=('Arial', 10)).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Edit Prescriptions", command=lambda: edit_prescriptions(patient.get_email()), font=('Arial', 10)).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Reset Password", command=lambda: reset_password(patient.get_email()), font=('Arial', 10)).grid(row=0, column=2, padx=5)

        admin_screen.mainloop()

    def update_patient_conditions_for_admin(self, patient):
        """Admin can update patient's conditions."""
        def save_conditions():
            new_conditions = conditions_entry.get().split(',')
            patient.set_conditions(new_conditions)
            self.save_patients()
            update_window.destroy()

        update_window = tk.Tk()
        update_window.title(f"Update Conditions for {patient.get_name()}")

        tk.Label(update_window, text="New Conditions:", font=('Arial', 15)).pack(pady=10)
        conditions_entry = tk.Entry(update_window, font=('Arial', 15))
        conditions_entry.insert(0, ', '.join(patient.get_conditions()))
        conditions_entry.pack(pady=10)

        tk.Button(update_window, text="Save", command=save_conditions, font=('Arial', 15)).pack(pady=10)

        update_window.mainloop()

    def update_patient_prescriptions_for_admin(self, patient):
        """Admin can update patient's prescriptions."""
        def save_prescriptions():
            new_prescriptions = prescriptions_entry.get().split(',')
            patient.set_prescriptions(new_prescriptions)
            self.save_patients()
            update_window.destroy()

        update_window = tk.Tk()
        update_window.title(f"Update Prescriptions for {patient.get_name()}")

        tk.Label(update_window, text="New Prescriptions:", font=('Arial', 15)).pack(pady=10)
        prescriptions_entry = tk.Entry(update_window, font=('Arial', 15))
        prescriptions_entry.insert(0, ', '.join(patient.get_prescriptions()))
        prescriptions_entry.pack(pady=10)

        tk.Button(update_window, text="Save", command=save_prescriptions, font=('Arial', 15)).pack(pady=10)

        update_window.mainloop()

    def reset_patient_password(self, patient):
        """Allow admin to reset a patient's password."""
        def save_password():
            new_password = password_entry.get()
            if new_password:
                patient.set_password(new_password)
                self.save_patients()
                reset_window.destroy()
            else:
                messagebox.showerror("Error", "Please enter a new password!")

        reset_window = tk.Tk()
        reset_window.title(f"Reset Password for {patient.get_name()}")

        tk.Label(reset_window, text="New Password:", font=('Arial', 15)).pack(pady=10)
        password_entry = tk.Entry(reset_window, show="*", font=('Arial', 15))
        password_entry.pack(pady=10)

        tk.Button(reset_window, text="Save", command=save_password, font=('Arial', 15)).pack(pady=10)

        reset_window.mainloop()


# Run the app
if __name__ == "__main__":
    app = HealthCareApp()

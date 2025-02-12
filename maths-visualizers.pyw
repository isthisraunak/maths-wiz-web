import sys
import random
import math
import time
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QMessageBox, QTabWidget, QComboBox, QFileDialog
)
from PyQt5.QtCore import QTimer

# For 3D plotting in Lorenz Attractor:
from mpl_toolkits.mplot3d import Axes3D

# For PDF report generation:
from fpdf import FPDF

##############################################
# Tab 1: Collatz Conjecture Visualizer
##############################################
def collatz_sequence(n):
    seq = [n]
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        seq.append(n)
    return seq

class CollatzVisualizerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.layout = QVBoxLayout(self)
        
        self.label = QLabel("Enter a positive integer for Collatz visualization:", self)
        self.layout.addWidget(self.label)
        self.input_field = QLineEdit(self)
        self.layout.addWidget(self.input_field)
        
        self.visualize_button = QPushButton("Visualize Collatz Sequence", self)
        self.visualize_button.clicked.connect(self.start_visualization)
        self.layout.addWidget(self.visualize_button)
        
        self.status_label = QLabel("Status: Waiting for input...", self)
        self.layout.addWidget(self.status_label)
        
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        
        self.sequence = []
        self.current_index = 0
        self.start_time = None

    def start_visualization(self):
        try:
            start_num = int(self.input_field.text())
            if start_num <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Input Error", "Enter a valid positive integer!")
            return
        
        self.sequence = collatz_sequence(start_num)
        self.current_index = 0
        self.start_time = time.time()
        
        self.ax.clear()
        self.ax.set_title(f"Collatz Sequence starting at {start_num}")
        self.ax.set_xlabel("Step")
        self.ax.set_ylabel("Value")
        self.ax.grid(True)
        self.canvas.draw()
        
        self.timer.start(300)

    def update_plot(self):
        elapsed = time.time() - self.start_time if self.start_time else 0
        if self.current_index < len(self.sequence):
            x_vals = list(range(self.current_index + 1))
            y_vals = self.sequence[:self.current_index + 1]
            self.ax.clear()
            self.ax.plot(x_vals, y_vals, marker='o', linestyle='-', color='blue')
            self.ax.set_title(f"Collatz Sequence (Step {self.current_index+1} of {len(self.sequence)})")
            self.ax.set_xlabel("Step")
            self.ax.set_ylabel("Value")
            self.ax.grid(True)
            self.canvas.draw()
            self.current_index += 1
            self.status_label.setText(f"Step: {self.current_index}/{len(self.sequence)} | Time: {elapsed:.2f} sec")
        else:
            self.timer.stop()
            self.status_label.setText(f"Completed in {elapsed:.2f} sec. Final value: {self.sequence[-1]}")

##############################################
# Tab 2: Pi Approximator Multi-Method
##############################################
class PiApproximatorMultiMethodWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.layout = QVBoxLayout(self)
        
        controls_layout = QHBoxLayout()
        self.method_combo = QComboBox(self)
        self.method_combo.addItems(["Monte Carlo", "Leibniz Series", "Nilakantha Series", "All Methods"])
        controls_layout.addWidget(QLabel("Select Method:", self))
        controls_layout.addWidget(self.method_combo)
        
        self.iteration_input = QLineEdit(self)
        self.iteration_input.setPlaceholderText("e.g., 10000")
        controls_layout.addWidget(QLabel("Iterations/Points:", self))
        controls_layout.addWidget(self.iteration_input)
        
        self.start_button = QPushButton("Start Simulation", self)
        self.start_button.clicked.connect(self.start_simulation)
        controls_layout.addWidget(self.start_button)
        
        self.pdf_button = QPushButton("Generate PDF Report", self)
        self.pdf_button.clicked.connect(self.generate_pdf_report)
        controls_layout.addWidget(self.pdf_button)
        
        self.layout.addLayout(controls_layout)
        
        self.status_label = QLabel("Status: Waiting for input...", self)
        self.layout.addWidget(self.status_label)
        
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        
        self.total_iterations = 0
        self.current_iteration = 0
        self.x_data = []
        self.y_data = []
        self.selected_method = None
        
        self.mc_total = 0
        self.mc_inside = 0
        
        self.lei_sum = 0.0
        self.nila_sum = 3.0
        
        self.mc_y_data = []
        self.lei_y_data = []
        self.nila_y_data = []
        
        self.start_time = None

    def start_simulation(self):
        try:
            self.total_iterations = int(self.iteration_input.text())
            if self.total_iterations <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Input Error", "Enter a valid positive integer for iterations!")
            return
        
        self.selected_method = self.method_combo.currentText()
        self.current_iteration = 0
        self.x_data = []
        self.y_data = []
        self.mc_y_data = []
        self.lei_y_data = []
        self.nila_y_data = []
        self.start_time = time.time()
        self.status_label.setText("Starting simulation using " + self.selected_method)
        
        if self.selected_method in ["Monte Carlo", "All Methods"]:
            self.mc_total = 0
            self.mc_inside = 0
        if self.selected_method in ["Leibniz Series", "All Methods"]:
            self.lei_sum = 0.0
        if self.selected_method in ["Nilakantha Series", "All Methods"]:
            self.nila_sum = 3.0
        
        self.ax.clear()
        self.ax.set_title(f"{self.selected_method} - Pi Approximation Convergence")
        self.ax.set_xlabel("Iteration")
        self.ax.set_ylabel("Approximation of Pi")
        self.ax.grid(True)
        self.canvas.draw()
        
        self.timer.start(10)

    def update_simulation(self):
        if self.current_iteration >= self.total_iterations:
            self.timer.stop()
            elapsed = time.time() - self.start_time
            final_text = f"Completed in {elapsed:.2f} sec. "
            if self.selected_method == "Monte Carlo":
                pi_val = 4 * self.mc_inside / self.mc_total if self.mc_total else 0
                final_text += f"Monte Carlo: Pi ≈ {pi_val:.6f}"
            elif self.selected_method == "Leibniz Series":
                pi_val = 4 * self.lei_sum
                final_text += f"Leibniz Series: Pi ≈ {pi_val:.6f}"
            elif self.selected_method == "Nilakantha Series":
                pi_val = self.nila_sum
                final_text += f"Nilakantha Series: Pi ≈ {pi_val:.6f}"
            elif self.selected_method == "All Methods":
                mc_val = 4 * self.mc_inside / self.mc_total if self.mc_total else 0
                lei_val = 4 * self.lei_sum
                nila_val = self.nila_sum
                final_text += (f"Monte Carlo: Pi ≈ {mc_val:.6f} | "
                              f"Leibniz: Pi ≈ {lei_val:.6f} | "
                              f"Nilakantha: Pi ≈ {nila_val:.6f}")
            self.status_label.setText(final_text)
            return
        
        self.current_iteration += 1
        self.x_data.append(self.current_iteration)
        elapsed = time.time() - self.start_time
        
        if self.selected_method == "Monte Carlo":
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            self.mc_total += 1
            if x*x + y*y <= 1:
                self.mc_inside += 1
            pi_approx = 4 * self.mc_inside / self.mc_total
            self.y_data.append(pi_approx)
            error = abs(math.pi - pi_approx)
            status = f"Iteration: {self.current_iteration}/{self.total_iterations} | Pi ≈ {pi_approx:.6f} | Err: {error:.6f} | Time: {elapsed:.2f} sec"
        
        elif self.selected_method == "Leibniz Series":
            term = ((-1) ** (self.current_iteration - 1)) / (2 * (self.current_iteration - 1) + 1) if self.current_iteration > 0 else 1
            self.lei_sum += term
            pi_approx = 4 * self.lei_sum
            self.y_data.append(pi_approx)
            error = abs(math.pi - pi_approx)
            status = f"Iteration: {self.current_iteration}/{self.total_iterations} | Pi ≈ {pi_approx:.6f} | Err: {error:.6f} | Time: {elapsed:.2f} sec"
        
        elif self.selected_method == "Nilakantha Series":
            i = self.current_iteration
            term = 4 / ((2 * i) * (2 * i + 1) * (2 * i + 2))
            if i % 2 == 0:
                term = -term
            self.nila_sum += term
            pi_approx = self.nila_sum
            self.y_data.append(pi_approx)
            error = abs(math.pi - pi_approx)
            status = f"Iteration: {self.current_iteration}/{self.total_iterations} | Pi ≈ {pi_approx:.6f} | Err: {error:.6f} | Time: {elapsed:.2f} sec"
        
        elif self.selected_method == "All Methods":
            x_mc = random.uniform(-1, 1)
            y_mc = random.uniform(-1, 1)
            self.mc_total += 1
            if x_mc*x_mc + y_mc*y_mc <= 1:
                self.mc_inside += 1
            mc_val = 4 * self.mc_inside / self.mc_total
            self.mc_y_data.append(mc_val)
            
            term = ((-1) ** (self.current_iteration - 1)) / (2 * (self.current_iteration - 1) + 1) if self.current_iteration > 0 else 1
            self.lei_sum += term
            lei_val = 4 * self.lei_sum
            self.lei_y_data.append(lei_val)
            
            i = self.current_iteration
            term2 = 4 / ((2 * i) * (2 * i + 1) * (2 * i + 2))
            if i % 2 == 0:
                term2 = -term2
            self.nila_sum += term2
            nila_val = self.nila_sum
            self.nila_y_data.append(nila_val)
            
            error_mc = abs(math.pi - mc_val)
            error_lei = abs(math.pi - lei_val)
            error_nila = abs(math.pi - nila_val)
            status = (f"Iteration: {self.current_iteration}/{self.total_iterations} | "
                      f"MC: {mc_val:.6f} (err {error_mc:.6f}), "
                      f"Leibniz: {lei_val:.6f} (err {error_lei:.6f}), "
                      f"Nilakantha: {nila_val:.6f} (err {error_nila:.6f}) | "
                      f"Time: {elapsed:.2f} sec")
        
        self.status_label.setText(status)
        self.ax.clear()
        if self.selected_method != "All Methods":
            self.ax.plot(self.x_data, self.y_data, color='blue', marker='o', markersize=2, linestyle='-')
        else:
            self.ax.plot(self.x_data, self.mc_y_data, color='green', marker='o', markersize=2, linestyle='-', label='Monte Carlo')
            self.ax.plot(self.x_data, self.lei_y_data, color='blue', marker='o', markersize=2, linestyle='-', label='Leibniz Series')
            self.ax.plot(self.x_data, self.nila_y_data, color='red', marker='o', markersize=2, linestyle='-', label='Nilakantha Series')
            self.ax.legend(loc='upper right')
        self.ax.set_title(f"{self.selected_method} - Pi Approximation Convergence")
        self.ax.set_xlabel("Iteration")
        self.ax.set_ylabel("Approximation of Pi")
        self.ax.grid(True)
        self.canvas.draw()

    def generate_pdf_report(self):
        self.timer.stop()
        elapsed = time.time() - self.start_time if self.start_time else 0
        report_text = f"Pi Approximation Report\n\nMethod: {self.selected_method}\n"
        report_text += f"Total Iterations: {self.current_iteration}\n"
        report_text += f"Elapsed Time: {elapsed:.2f} seconds\n\n"
        if self.selected_method == "Monte Carlo":
            pi_val = 4 * self.mc_inside / self.mc_total if self.mc_total else 0
            report_text += f"Final Approximation (Monte Carlo): {pi_val:.6f}\n"
            report_text += f"Error: {abs(math.pi - pi_val):.6f}\n"
        elif self.selected_method == "Leibniz Series":
            pi_val = 4 * self.lei_sum
            report_text += f"Final Approximation (Leibniz Series): {pi_val:.6f}\n"
            report_text += f"Error: {abs(math.pi - pi_val):.6f}\n"
        elif self.selected_method == "Nilakantha Series":
            pi_val = self.nila_sum
            report_text += f"Final Approximation (Nilakantha Series): {pi_val:.6f}\n"
            report_text += f"Error: {abs(math.pi - pi_val):.6f}\n"
        elif self.selected_method == "All Methods":
            mc_val = 4 * self.mc_inside / self.mc_total if self.mc_total else 0
            lei_val = 4 * self.lei_sum
            nila_val = self.nila_sum
            report_text += f"Final Approximations:\n"
            report_text += f"Monte Carlo: {mc_val:.6f} (Error: {abs(math.pi - mc_val):.6f})\n"
            report_text += f"Leibniz Series: {lei_val:.6f} (Error: {abs(math.pi - lei_val):.6f})\n"
            report_text += f"Nilakantha Series: {nila_val:.6f} (Error: {abs(math.pi - nila_val):.6f})\n"
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "", "PDF Files (*.pdf)", options=options)
        if file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in report_text.split('\n'):
                pdf.cell(0, 10, line, ln=True)
            try:
                pdf.output(file_path)
                QMessageBox.information(self, "PDF Saved", f"Report saved successfully at:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "PDF Error", f"An error occurred while saving PDF:\n{e}")

##############################################
# Tab 3: Fractal Explorer (Mandelbrot) with Zoom
##############################################
class FractalExplorerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800,600)
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Mandelbrot Fractal Explorer", self)
        self.layout.addWidget(self.label)
        
        self.iter_input = QLineEdit(self)
        self.iter_input.setPlaceholderText("Max Iterations (e.g., 100)")
        self.layout.addWidget(self.iter_input)
        
        zoom_layout = QHBoxLayout()
        self.zoom_in_button = QPushButton("Zoom In", self)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.zoom_in_button)
        self.zoom_out_button = QPushButton("Zoom Out", self)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_out_button)
        self.reset_button = QPushButton("Reset View", self)
        self.reset_button.clicked.connect(self.reset_view)
        zoom_layout.addWidget(self.reset_button)
        self.layout.addLayout(zoom_layout)
        
        self.render_button = QPushButton("Render Mandelbrot", self)
        self.render_button.clicked.connect(self.render_fractal)
        self.layout.addWidget(self.render_button)
        
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        self.xmin, self.xmax = -2.0, 1.0
        self.ymin, self.ymax = -1.5, 1.5

    def render_fractal(self):
        try:
            max_iter = int(self.iter_input.text())
            if max_iter <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Input Error", "Enter a valid positive integer for max iterations!")
            return
        
        width, height = 400, 400
        x = np.linspace(self.xmin, self.xmax, width)
        y = np.linspace(self.ymin, self.ymax, height)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y
        Z = np.zeros_like(C)
        div_time = np.zeros(C.shape, dtype=int)
        for i in range(max_iter):
            Z = Z**2 + C
            diverge = np.abs(Z) > 2
            div_now = diverge & (div_time == 0)
            div_time[div_now] = i
            Z[diverge] = 2
        self.ax.clear()
        self.ax.imshow(div_time, cmap="hot", extent=[self.xmin, self.xmax, self.ymin, self.ymax])
        self.ax.set_title("Mandelbrot Set")
        self.canvas.draw()

    def zoom_in(self):
        x_center = (self.xmin + self.xmax) / 2
        y_center = (self.ymin + self.ymax) / 2
        x_range = (self.xmax - self.xmin) / 4
        y_range = (self.ymax - self.ymin) / 4
        self.xmin, self.xmax = x_center - x_range, x_center + x_range
        self.ymin, self.ymax = y_center - y_range, y_center + y_range
        self.render_fractal()

    def zoom_out(self):
        x_center = (self.xmin + self.xmax) / 2
        y_center = (self.ymin + self.ymax) / 2
        x_range = (self.xmax - self.xmin)
        y_range = (self.ymax - self.ymin)
        self.xmin -= x_range / 2
        self.xmax += x_range / 2
        self.ymin -= y_range / 2
        self.ymax += y_range / 2
        self.render_fractal()

    def reset_view(self):
        self.xmin, self.xmax = -2.0, 1.0
        self.ymin, self.ymax = -1.5, 1.5
        self.render_fractal()

##############################################
# Tab 4: Lorenz Attractor Visualizer
##############################################
class LorenzAttractorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800,600)
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Lorenz Attractor", self)
        self.layout.addWidget(self.label)
        self.start_button = QPushButton("Start Lorenz Attractor", self)
        self.start_button.clicked.connect(self.start_simulation)
        self.layout.addWidget(self.start_button)
        self.figure = plt.figure()
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.dt = 0.01
        self.sigma = 10.0
        self.rho = 28.0
        self.beta = 8.0 / 3.0
        self.x, self.y, self.z = 1.0, 1.0, 1.0
        self.x_data, self.y_data, self.z_data = [], [], []
    
    def start_simulation(self):
        self.x, self.y, self.z = 1.0, 1.0, 1.0
        self.x_data, self.y_data, self.z_data = [self.x], [self.y], [self.z]
        self.ax.clear()
        self.ax.set_title("Lorenz Attractor")
        self.timer.start(10)
    
    def update_simulation(self):
        dx = self.sigma * (self.y - self.x) * self.dt
        dy = (self.x * (self.rho - self.z) - self.y) * self.dt
        dz = (self.x * self.y - self.beta * self.z) * self.dt
        self.x += dx
        self.y += dy
        self.z += dz
        self.x_data.append(self.x)
        self.y_data.append(self.y)
        self.z_data.append(self.z)
        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data, self.z_data, color="purple")
        self.ax.set_title("Lorenz Attractor")
        self.canvas.draw()

##############################################
# Tab 5: Logistic Map Visualizer
##############################################
class LogisticMapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800,600)
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Logistic Map Visualizer", self)
        self.layout.addWidget(self.label)
        self.r_input = QLineEdit(self)
        self.r_input.setPlaceholderText("Parameter r (e.g., 3.7)")
        self.layout.addWidget(self.r_input)
        self.x0_input = QLineEdit(self)
        self.x0_input.setPlaceholderText("Initial x (e.g., 0.5)")
        self.layout.addWidget(self.x0_input)
        self.iter_input = QLineEdit(self)
        self.iter_input.setPlaceholderText("Iterations (e.g., 100)")
        self.layout.addWidget(self.iter_input)
        self.start_button = QPushButton("Start Logistic Map", self)
        self.start_button.clicked.connect(self.start_simulation)
        self.layout.addWidget(self.start_button)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.x_data = []
        self.y_data = []
        self.current_iteration = 0
        self.total_iterations = 0
        self.r = 3.7
        self.x = 0.5
    
    def start_simulation(self):
        try:
            self.r = float(self.r_input.text())
            self.x = float(self.x0_input.text())
            self.total_iterations = int(self.iter_input.text())
            if self.total_iterations <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Input Error", "Enter valid numbers for r, initial x, and iterations!")
            return
        self.x_data = [0]
        self.y_data = [self.x]
        self.current_iteration = 0
        self.ax.clear()
        self.ax.set_title("Logistic Map")
        self.ax.set_xlabel("Iteration")
        self.ax.set_ylabel("x value")
        self.ax.grid(True)
        self.canvas.draw()
        self.timer.start(50)
    
    def update_simulation(self):
        if self.current_iteration >= self.total_iterations:
            self.timer.stop()
            return
        self.current_iteration += 1
        self.x = self.r * self.x * (1 - self.x)
        self.x_data.append(self.current_iteration)
        self.y_data.append(self.x)
        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data, marker='o', linestyle='-', color='orange')
        self.ax.set_title("Logistic Map")
        self.ax.set_xlabel("Iteration")
        self.ax.set_ylabel("x value")
        self.ax.grid(True)
        self.canvas.draw()

##############################################
# Tab 6: Van der Pol Oscillator Visualizer
##############################################
class VanDerPolWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800,600)
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Van der Pol Oscillator", self)
        self.layout.addWidget(self.label)
        self.mu_input = QLineEdit(self)
        self.mu_input.setPlaceholderText("Mu (e.g., 1.0)")
        self.layout.addWidget(self.mu_input)
        self.start_button = QPushButton("Start Simulation", self)
        self.start_button.clicked.connect(self.start_simulation)
        self.layout.addWidget(self.start_button)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.dt = 0.01
        self.mu = 1.0
        self.x = 2.0
        self.y = 0.0
        self.x_data = [self.x]
        self.y_data = [self.y]
        self.current_iteration = 0
        self.total_iterations = 1000

    def start_simulation(self):
        try:
            self.mu = float(self.mu_input.text())
            self.total_iterations = 1000
        except:
            QMessageBox.warning(self, "Input Error", "Enter a valid number for mu!")
            return
        self.x = 2.0
        self.y = 0.0
        self.x_data = [self.x]
        self.y_data = [self.y]
        self.current_iteration = 0
        self.ax.clear()
        self.ax.set_title("Van der Pol Oscillator (Phase Space)")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.grid(True)
        self.canvas.draw()
        self.timer.start(10)

    def update_simulation(self):
        if self.current_iteration >= self.total_iterations:
            self.timer.stop()
            return
        self.current_iteration += 1
        dx = self.y * self.dt
        dy = (self.mu * (1 - self.x**2) * self.y - self.x) * self.dt
        self.x += dx
        self.y += dy
        self.x_data.append(self.x)
        self.y_data.append(self.y)
        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data, color='magenta')
        self.ax.set_title("Van der Pol Oscillator (Phase Space)")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.grid(True)
        self.canvas.draw()

##############################################
# Tab 7: Fibonacci & Golden Spiral Visualizer
##############################################
class FibonacciSpiralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800,600)
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Fibonacci & Golden Spiral", self)
        self.layout.addWidget(self.label)
        self.iter_input = QLineEdit(self)
        self.iter_input.setPlaceholderText("Number of squares (e.g., 10)")
        self.layout.addWidget(self.iter_input)
        self.render_button = QPushButton("Render Spiral", self)
        self.render_button.clicked.connect(self.render_spiral)
        self.layout.addWidget(self.render_button)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
    
    def render_spiral(self):
        try:
            n = int(self.iter_input.text())
            if n <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Input Error", "Enter a valid positive integer for number of squares!")
            return
        self.ax.clear()
        fib = [0, 1]
        for i in range(2, n+2):
            fib.append(fib[-1] + fib[-2])
        squares = []
        x, y = 0, 0
        angle = 0
        for i in range(n):
            side = fib[i+1]
            squares.append((x, y, side, angle))
            if angle == 0:
                x += side
            elif angle == 90:
                y += side
            elif angle == 180:
                x -= side
            elif angle == 270:
                y -= side
            angle = (angle + 90) % 360
        
        import matplotlib.patches as patches
        for (x, y, side, ang) in squares:
            rect = patches.Rectangle((x, y), side, side, linewidth=1, edgecolor='black', facecolor='none')
            self.ax.add_patch(rect)
        theta = np.linspace(0, np.pi/2, 100)
        for (x, y, side, ang) in squares:
            if ang == 0:
                xc, yc = x, y
            elif ang == 90:
                xc, yc = x, y
            elif ang == 180:
                xc, yc = x + side, y + side
            elif ang == 270:
                xc, yc = x + side, y + side
            arc_x = xc + side * np.cos(theta)
            arc_y = yc + side * np.sin(theta)
            self.ax.plot(arc_x, arc_y, color='green')
        self.ax.set_aspect('equal')
        self.ax.set_title("Fibonacci & Golden Spiral")
        self.canvas.draw()

##############################################
# Tab 8: Newton Fractal Visualizer with Zoom
##############################################
class NewtonFractalWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800,600)
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Newton Fractal Visualizer", self)
        self.layout.addWidget(self.label)
        self.iter_input = QLineEdit(self)
        self.iter_input.setPlaceholderText("Max Iterations (e.g., 50)")
        self.layout.addWidget(self.iter_input)
        
        zoom_layout = QHBoxLayout()
        self.zoom_in_button = QPushButton("Zoom In", self)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.zoom_in_button)
        self.zoom_out_button = QPushButton("Zoom Out", self)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_out_button)
        self.reset_button = QPushButton("Reset View", self)
        self.reset_button.clicked.connect(self.reset_view)
        zoom_layout.addWidget(self.reset_button)
        self.layout.addLayout(zoom_layout)
        
        self.render_button = QPushButton("Render Newton Fractal", self)
        self.render_button.clicked.connect(self.render_fractal)
        self.layout.addWidget(self.render_button)
        
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        self.xmin, self.xmax = -2.0, 2.0
        self.ymin, self.ymax = -2.0, 2.0

    def render_fractal(self):
        try:
            max_iter = int(self.iter_input.text())
            if max_iter <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Input Error", "Enter a valid positive integer for max iterations!")
            return
        
        re = np.linspace(self.xmin, self.xmax, 400)
        im = np.linspace(self.ymin, self.ymax, 400)
        Re, Im = np.meshgrid(re, im)
        Z = Re + 1j * Im
        fractal = np.zeros(Z.shape, dtype=int)
        for i in range(max_iter):
            Z = Z - (Z**3 - 1) / (3 * Z**2)
            converged = np.abs(Z**3 - 1) < 1e-6
            fractal[converged] = i
        self.ax.clear()
        self.ax.imshow(fractal, cmap="inferno", extent=[self.xmin, self.xmax, self.ymin, self.ymax])
        self.ax.set_title("Newton Fractal for f(z)=z^3 - 1")
        self.canvas.draw()

    def zoom_in(self):
        x_center = (self.xmin + self.xmax) / 2
        y_center = (self.ymin + self.ymax) / 2
        x_range = (self.xmax - self.xmin) / 4
        y_range = (self.ymax - self.ymin) / 4
        self.xmin, self.xmax = x_center - x_range, x_center + x_range
        self.ymin, self.ymax = y_center - y_range, y_center + y_range
        self.render_fractal()

    def zoom_out(self):
        x_center = (self.xmin + self.xmax) / 2
        y_center = (self.ymin + self.ymax) / 2
        x_range = (self.xmax - self.xmin)
        y_range = (self.ymax - self.ymin)
        self.xmin -= x_range / 2
        self.xmax += x_range / 2
        self.ymin -= y_range / 2
        self.ymax += y_range / 2
        self.render_fractal()

    def reset_view(self):
        self.xmin, self.xmax = -2.0, 2.0
        self.ymin, self.ymax = -2.0, 2.0
        self.render_fractal()

##############################################
# Tab 9: Prime Number Distribution Visualizer
##############################################
class PrimeDistributionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800,600)
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Prime Number Distribution", self)
        self.layout.addWidget(self.label)
        self.num_input = QLineEdit(self)
        self.num_input.setPlaceholderText("Max Number (e.g., 1000)")
        self.layout.addWidget(self.num_input)
        self.render_button = QPushButton("Render Prime Distribution", self)
        self.render_button.clicked.connect(self.render_distribution)
        self.layout.addWidget(self.render_button)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
    
    def is_prime(self, n):
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    def render_distribution(self):
        try:
            max_num = int(self.num_input.text())
            if max_num < 2:
                raise ValueError
        except:
            QMessageBox.warning(self, "Input Error", "Enter a valid integer greater than 1!")
            return
        primes = [n for n in range(2, max_num + 1) if self.is_prime(n)]
        self.ax.clear()
        self.ax.scatter(primes, [1] * len(primes), color='blue', marker='o')
        self.ax.set_title(f"Prime Numbers up to {max_num}")
        self.ax.set_xlabel("Number")
        self.ax.set_yticks([])
        self.canvas.draw()

##############################################
# Main Application with Tabs
##############################################
class CombinedVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mathematical Visualizers")
        self.setGeometry(50, 50, 1000, 800)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.tabs.addTab(CollatzVisualizerWidget(), "Collatz Visualizer")
        self.tabs.addTab(PiApproximatorMultiMethodWidget(), "Pi Approximator")
        self.tabs.addTab(FractalExplorerWidget(), "Fractal Explorer")
        self.tabs.addTab(LorenzAttractorWidget(), "Lorenz Attractor")
        self.tabs.addTab(LogisticMapWidget(), "Logistic Map")
        self.tabs.addTab(VanDerPolWidget(), "Van der Pol Oscillator")
        self.tabs.addTab(FibonacciSpiralWidget(), "Fibonacci & Spiral")
        self.tabs.addTab(NewtonFractalWidget(), "Newton Fractal")
        self.tabs.addTab(PrimeDistributionWidget(), "Prime Distribution")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CombinedVisualizer()
    window.show()
    sys.exit(app.exec_())

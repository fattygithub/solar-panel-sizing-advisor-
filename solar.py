from flask import Flask, render_template, request # type: ignore
import math
import os

app = Flask(__name__)

# Mock irradiance lookup table (kWh/m^2/day)
IRRADIANCE_TABLE = {
    'Lagos': 5.0,
    'Abuja': 5.5,
    'Kano': 6.0,
    'Port Harcourt': 4.5
}

# Mock solar panel database
SOLAR_PANELS = [
    {'model': 'Panel A', 'watt': 330, 'efficiency': 0.18, 'cost': 200},
    {'model': 'Panel B', 'watt': 400, 'efficiency': 0.20, 'cost': 250},
    {'model': 'Panel C', 'watt': 450, 'efficiency': 0.22, 'cost': 300},
]

# Helper to calculate daily energy usage in kWh
def calculate_daily_energy(monthly_kwh):
    return monthly_kwh / 30.0

# Helper to calculate number of panels needed
def calculate_panels(daily_energy, irradiance, panel):
    daily_output_per_panel = (panel['watt'] / 1000.0) * irradiance
    num_panels = math.ceil(daily_energy / daily_output_per_panel)
    return num_panels

# Estimate cost, savings, ROI
def estimate_costs_savings(num_panels, panel):
    system_cost = num_panels * panel['cost']
    yearly_savings = 12 * 30 * (panel['watt'] / 1000.0) * 5.0 * 0.15  # kWh * rate (Naira)
    roi_years = round(system_cost / yearly_savings, 1)
    return system_cost, yearly_savings, roi_years

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        try:
            location = request.form['location']
            roof_area = float(request.form['roof_area'])
            monthly_kwh = float(request.form['monthly_kwh'])

            irradiance = IRRADIANCE_TABLE.get(location, 5.0)
            daily_energy = calculate_daily_energy(monthly_kwh)

            best_option = None
            for panel in SOLAR_PANELS:
                num_panels = calculate_panels(daily_energy, irradiance, panel)
                total_area = num_panels * (1.7 * 1.0)  # assuming each panel ~1.7m x 1.0m
                if total_area <= roof_area:
                    system_cost, yearly_savings, roi = estimate_costs_savings(num_panels, panel)
                    best_option = {
                        'panel': panel,
                        'num_panels': num_panels,
                        'system_cost': system_cost,
                        'yearly_savings': yearly_savings,
                        'roi': roi,
                        'total_area': total_area
                    }
                    break

            result = best_option
        except Exception as e:
            result = {'error': f"An error occurred: {str(e)}"}

    return render_template('index.html', result=result, locations=IRRADIANCE_TABLE.keys())

if __name__ == '__main__':
    # Bind to 0.0.0.0 and use port from environment or default to 5000 for wider compatibility
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

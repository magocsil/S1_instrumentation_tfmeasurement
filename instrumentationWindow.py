from tkinter import *
import pyvisa as visa
import tkinter.messagebox
import tkinter.ttk as ttk
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename
import matplotlib as mpl
mpl.rcParams["savefig.directory"] = ""
mpl.rcParams["savefig.format"] = "png"
mpl.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import sys
import math


main_window = Tk()
main_window.title("Transfer function measurement")
main_window.resizable(False, False)

visa.log_to_screen()
rm = visa.ResourceManager('@py')

device_list = list()
is_running = False
next_task = int()
isNot33120A = False
memory_list = list()
freq_list = list()
freq_in_list = list()
voltage_in_list = list()
voltage_out_list = list()
phase_difference_list = list()
gain_list = list()
channel_in = ""
channel_out = ""
kmin = -1
kmax = 1
limits_frequency = [20, 20000]
limits_gain = [0, 1.2]
limits_phase = [-90, 90]
steps_phase = 45
ticks_phase = [-90, -45, 0, 45, 90]
labels_phase = [f'{x}' for x in ticks_phase]
boolean_var_gain_in_db = BooleanVar()
boolean_var_gain_in_db.set(False)
boolean_var_phase_in_radians = BooleanVar()
boolean_var_phase_in_radians.set(False)
measurement_unit_gain = ""
measurement_unit_phase_difference = " [°]"
csv_details = [("Comma-separated values (*.csv)","*.csv")]

def ListResources():
	global device_list
	global combobox_fg
	global combobox_scope
	
	device_list = sorted(rm.list_resources(), reverse=True)
	
	combobox_fg['values'] = device_list
	combobox_scope['values'] = device_list
	if (combobox_fg.get() is None) or (combobox_fg.get() == ""):
		combobox_fg.set(device_list[1])
	if (combobox_scope.get() is None) or (combobox_scope.get() == ""):
		combobox_scope.set(device_list[0])

def FunctionGainLimitsdB():
	global limits_gain
	global gain_list
	minimal_gain = -10
	maximal_gain = 0
	if len(gain_list) > 0:
		minimal_gain = min(gain_list)
		maximal_gain = max(gain_list)
	if len(memory_list) > 0:
		for i in range(int(len(memory_list) / 3)):
			minimal_gain = min(minimal_gain, min(memory_list[i * 3 + 1]))
			maximal_gain = max(maximal_gain, max(memory_list[i * 3 + 1]))
	try:
		limits_gain = [minimal_gain, maximal_gain + 1.2]
	except:
		limits_gain = [minimal_gain, maximal_gain + 1.2]

def FunctionGainLimitsNodB():
	global limits_gain
	global gain_list
	minimal_gain = 0
	maximal_gain = 1
	if len(gain_list) > 0:
		minimal_gain = min(gain_list)
		maximal_gain = max(gain_list)
	if len(memory_list) > 0:
		for i in range(int(len(memory_list) / 3)):
			minimal_gain = min(minimal_gain, min(memory_list[i * 3 + 1]))
			maximal_gain = max(maximal_gain, max(memory_list[i * 3 + 1]))
	try:
		limits_gain = [0, max(1.2, maximal_gain + 0.2)]
	except:
		limits_gain = [minimal_gain, maximal_gain + 0.2]

def FunctionUpdateGain():
	global measurement_unit_gain
	global gain_list
	if boolean_var_gain_in_db.get():
		if len(memory_list) > 0:
			for i in range(0, int(len(memory_list) / 3)):
				temp = [20 * math.log(x, 10) for x in memory_list[i * 3 + 1]]
				memory_list[i * 3 + 1] = temp
		result = [20 * math.log(x, 10) for x in gain_list]
		gain_list = result
		measurement_unit_gain = " [dB]"
		FunctionGainLimitsdB()
	else:
		if len(memory_list) > 0:
			for i in range(0, int(len(memory_list) / 3)):
				temp = [10 ** (x / 20) for x in memory_list[i * 3 + 1]]
				memory_list[i * 3 + 1] = temp
		result = [10 ** (x / 20) for x in gain_list]
		gain_list = result
		measurement_unit_gain = ""
		FunctionGainLimitsNodB()
	FunctionDisplay()

def FunctionPhaseLimitsRad():
	global limits_phase
	global phase_difference_list
	global kmin
	global kmax
	global ticks_phase
	global labels_phase
	global steps_phase
	steps_phase = math.pi / 4
	minimal_phase = 0
	maximal_phase = 0
	if len(phase_difference_list) > 0:
		minimal_phase = min(phase_difference_list)
		maximal_phase = max(phase_difference_list)
	if len(memory_list) > 0:
		for i in range(int(len(memory_list) / 3)):
			minimal_phase = min(minimal_phase, min(memory_list[i * 3 + 2]))
			maximal_phase = max(maximal_phase, max(memory_list[i * 3 + 2]))
	try:
		while kmin * math.pi / 2 > min(phase_difference_list):
			kmin = kmin - 1
		while kmax * math.pi / 2 < max(phase_difference_list):
			kmax = kmax + 1
	except:
		if len(memory_list) == 0:
			kmin = -1
			kmax = 1
	limits_phase = [kmin / 2 * math.pi, kmax / 2 * math.pi]
	ticks_phase = [x * math.pi / 4 for x in range(kmin * 2, kmax * 2 + 1)]
	labels_phase = ['0' if x == 0 else f'{x}π/4' for x in range(kmin * 2, kmax * 2 + 1)]

def FunctionPhaseLimitsDeg():
	global limits_phase
	global phase_difference_list
	global kmin
	global kmax
	global ticks_phase
	global labels_phase
	global steps_phase
	steps_phase = 45
	minimal_phase = 0
	maximal_phase = 0
	if len(phase_difference_list) > 0:
		minimal_phase = min(phase_difference_list)
		maximal_phase = max(phase_difference_list)
	if len(memory_list) > 0:
		for i in range(int(len(memory_list) / 3)):
			minimal_phase = min(minimal_phase, min(memory_list[i * 3 + 2]))
			maximal_phase = max(maximal_phase, max(memory_list[i * 3 + 2]))
	try:
		while kmin * 90 > min(phase_difference_list):
			kmin = kmin - 1
		while kmax * 90 < max(phase_difference_list):
			kmax = kmax + 1
	except:
		if len(memory_list) == 0:
			kmin = -1
			kmax = 1
	limits_phase = [kmin * 90, kmax * 90]
	ticks_phase = range(limits_phase[0], limits_phase[1] + 1, steps_phase)
	labels_phase = [f'{x}' for x in ticks_phase]

def FunctionUpdatePhaseDifference():
	global measurement_unit_phase_difference
	global phase_difference_list
	global ticks_phase
	if boolean_var_phase_in_radians.get():
		if len(memory_list) > 0:
			for i in range(0, int(len(memory_list) / 3)):
				temp = [x / 180 * math.pi for x in memory_list[i * 3 + 2]]
				memory_list[i * 3 + 2] = temp
		result = [x / 180 * math.pi for x in phase_difference_list]
		phase_difference_list = result
		measurement_unit_phase_difference = " [rad]"
		FunctionPhaseLimitsRad()
	else:
		if len(memory_list) > 0:
			for i in range(0, int(len(memory_list) / 3)):
				temp = [x / math.pi * 180 for x in memory_list[i * 3 + 2]]
				memory_list[i * 3 + 2] = temp
		result = [x / math.pi * 180 for x in phase_difference_list]
		phase_difference_list = result
		measurement_unit_phase_difference = " [°]"
		FunctionPhaseLimitsDeg()
	
	FunctionDisplay()

def FunctionFinalizePlotLimits():
	if boolean_var_gain_in_db.get():
		FunctionGainLimitsdB()
	else:
		FunctionGainLimitsNodB()
	
	global kmin
	global kmax
	kmin = 0
	kmax = 0
	if boolean_var_phase_in_radians.get():
		FunctionPhaseLimitsRad()
	else:
		FunctionPhaseLimitsDeg()
	FunctionDisplay()
	
	if (len(freq_in_list) > 0):
		memory_list.append(freq_in_list)
		memory_list.append(gain_list)
		memory_list.append(phase_difference_list)
	FunctionClearCurrent()

def FunctionClearFormer():
	global memory_list
	memory_list = list()

def FunctionClearCurrent():
	global freq_in_list
	global voltage_in_list
	global voltage_out_list
	global gain_list
	global phase_difference_list
	freq_in_list = list()
	voltage_in_list = list()
	voltage_out_list = list()
	gain_list = list()
	phase_difference_list = list()

def FunctionClearFigure():
	FunctionClearFormer()
	
	if is_running:
		FunctionDisplay()
	else:
		FunctionFinalizePlotLimits()

def FunctionInitBode():
	subplot_gain.cla()
	subplot_phase.cla()
	subplot_gain.set_title('Gain', fontdict={'fontsize':10})
	subplot_gain.set_xlabel('f [Hz]')
	subplot_gain.set_xscale('log')
	subplot_gain.set_xlim(limits_frequency)
	subplot_gain.set_ylabel(f'A{measurement_unit_gain}', labelpad=-10)
	subplot_gain.xaxis.label.set_position((1, 0))
	subplot_gain.set_ylim(limits_gain)
	subplot_gain.yaxis.label.set_position((0, 1.05))
	subplot_gain.yaxis.label.set_rotation(0)
	subplot_gain.grid(which='both')
	subplot_phase.set_title('Phase', fontdict={'fontsize':10})
	subplot_phase.set_xlabel('f [Hz]')
	subplot_phase.set_xscale('log')
	subplot_phase.set_xlim(limits_frequency)
	subplot_phase.xaxis.label.set_position((1, 0))
	subplot_phase.set_ylabel(f'φ{measurement_unit_phase_difference}', labelpad=-15)
	subplot_phase.set_ylim(limits_phase)
	subplot_phase.yaxis.label.set_position((0, 1.05))
	subplot_phase.yaxis.label.set_rotation(0)
	subplot_phase.set_yticks(ticks_phase)
	subplot_phase.set_yticklabels(labels_phase)
	subplot_phase.grid(which='both')

def FunctionDisplay():
	try:
		limits_gain[0] = min(gain_list[-1], limits_gain[0])
		limits_gain[1] = max(gain_list[-1] + 0.2 + int(gain_in_decibels.get()), limits_gain[1])
		limits_phase[0] = min(int(phase_difference_list[-1] / FunctionCalcPhaseDifference(90)) - FunctionCalcPhaseDifference(90), limits_phase[0])
		limits_phase[1] = max(int(phase_difference_list[-1] / FunctionCalcPhaseDifference(90)) + FunctionCalcPhaseDifference(90), limits_phase[1])
	
	except:
		pass
	FunctionInitBode()
	if len(memory_list) > 0:
		for i in range(int(len(memory_list) / 3)):
			subplot_gain.plot(memory_list[i * 3], memory_list[i * 3 + 1])
			subplot_phase.plot(memory_list[i * 3], memory_list[i * 3 + 2])
	subplot_gain.plot(freq_in_list, gain_list)
	subplot_phase.plot(freq_in_list, phase_difference_list)
	plot_canvas.draw()

def FunctionCalcGain(gain):
	if boolean_var_gain_in_db.get():
		gain = 20 * math.log(gain, 10)
	
	return gain

def FunctionCalcPhaseDifference(phase):
	if boolean_var_phase_in_radians.get():
		phase = phase / 180 * math.pi
	
	return phase

def FunctionFrequencyChange(f, i, fg, scope, channel_in, channel_out, avg):
	global next_task
	freq_in_list.append(f)
	
	scope.write(f'MEAS:ITEM? VPP,CHAN{channel_in}')
	main_window.after(100, QueryVoltageIn(scope))
	scope.write(f'MEAS:ITEM? VPP,CHAN{channel_out}')
	main_window.after(100, QueryVoltageOut(scope))
	gain = 1
	try:
		gain = voltage_out_list[-1] / voltage_in_list[-1]
	except:
		if len(gain_list) > 0:
			gain = gain_list[-1]
		else:
			gain = 0.01
	gain_list.append(FunctionCalcGain(gain))
	scope.write('MEAS:ITEM? RPH')
	main_window.after(100, QueryPhaseDifference(scope))
	
	FunctionDisplay()
	
	i = i + 1
	if (i in range(0, len(freq_list))) and is_running:
		fg.write(f'FREQ {freq_list[i]}')
		UpdateScope(scope, voltage_in_list[-1], voltage_out_list[-1], channel_in, channel_out, f)
		next_task = main_window.after(FunctionCalculateDelay(1000, avg, freq_list[i]), FunctionFrequencyChange, freq_list[i], i, fg, scope, channel_in, channel_out, avg)
	else:
		FunctionStop()

def FunctionExport():
	if len(memory_list) == 0:
		return
	str_to_write = ""
	measurement_units = [" [Hz]", measurement_unit_gain, measurement_unit_phase_difference]
	for i in range(-3, 0):
		str_to_write = str_to_write + measurement_units[i] + ", " + str(memory_list[i]) + "\r\n"
	str_to_write = str_to_write.replace("[", "")
	str_to_write = str_to_write.replace("]", "")
	str_to_write = str_to_write.replace(" ", "")
	file_exported = asksaveasfilename(title="Export the last measurement results to...", initialfile="measurementdata.csv", filetypes=csv_details, defaultextension=csv_details)
	with open(file_exported, 'w') as file_to_write:
		file_to_write.write(str(str_to_write))

def FunctionImport():
	data = ""
	file_imported = askopenfilename(title="Import previously measured data...", filetypes=csv_details, defaultextension=csv_details)
	with open(file_imported, 'r') as file_to_read:
		data = file_to_read.read()
	data.replace(" ", "")
	data = data.split()
	imported_freq = data[0].split(",")
	imported_freq.pop(0)
	temp = [float(f) for f in imported_freq]
	imported_freq = temp
	imported_gain = data[1].split(",")
	imported_unit_gain = imported_gain.pop(0)
	temp = [float(a) for a in imported_gain]
	imported_gain = temp
	imported_phase = data[2].split(",")
	imported_unit_phase = imported_phase.pop(0)
	temp = [float(phi) for phi in imported_phase]
	imported_phase = temp
	if ((imported_unit_gain == "") and (measurement_unit_gain == " [dB]")) or ((imported_unit_gain == "dB") and (measurement_unit_gain == "")):
		checkbutton_db.invoke()
	if ((imported_unit_phase == "rad") and (measurement_unit_phase_difference == " [°]")) or ((imported_unit_phase == "°") and (measurement_unit_phase_difference == " [rad]")):
		checkbutton_rad.invoke()
	global freq_in_list
	global gain_list
	global phase_difference_list
	freq_in_list = imported_freq
	gain_list = imported_gain
	phase_difference_list = imported_phase
	if boolean_var_gain_in_db.get():
		FunctionGainLimitsdB()
	else:
		FunctionGainLimitsNodB()
	if boolean_var_phase_in_radians.get():
		FunctionPhaseLimitsRad()
	else:
		FunctionPhaseLimitsDeg()
	FunctionFinalizePlotLimits()

def FunctionDemo(f, i, avg):
	global next_task
	r = 330
	c = 0.00000047
	voltage_out = math.sqrt((1 + (2 * math.pi * f * r * c) ** 2)) / (1 + (2 * math.pi * f * r * c) ** 2) #1 kHz LPF: 330R 470n
	freq_in_list.append(f)
	voltage_in_list.append(1)
	voltage_out_list.append(voltage_out)
	gain_list.append(FunctionCalcGain(voltage_out))
	phase_difference_list.append(FunctionCalcPhaseDifference(math.atan(-2 * math.pi * f * r * c) / math.pi * 180))
	
	FunctionDisplay()
	
	i = i + 1
	if (i in range(0, len(freq_list))) and is_running:
		next_task = main_window.after(FunctionCalculateDelay(1000, avg, freq_list[i]), FunctionDemo, freq_list[i], i, avg)
	else:
		FunctionStop()


def QueryVoltageIn(scope):
	voltage_in_list.append(float(scope.read()))

def QueryVoltageOut(scope):
	voltage_out_list.append(float(scope.read()))

def QueryPhaseDifference(scope):
	phase = float(scope.read())
	if phase > 360 or phase < -360:
		if len(phase_difference_list) > 0:
			phase = phase_difference_list[-1]
		else:
			phase = 0
	
	phase_difference_list.append(FunctionCalcPhaseDifference(float(phase)))

def FunctionFrequencySet(integers, points):
	digits = 2
	result = set()
	while len(result) < points and not (digits == 3 and integers):
		steps = set()
		for i in range(0, points):
			step_float = 10 ** (i / points)
			step = round(step_float, 0) * int(integers) + round(step_float, digits) * int(not integers)
			steps.add(step)
		digits = digits + 1
		result = steps
	
	return result

def SetupFG(fg, voltage_in):
	global isNot33120A
	fg.write('*IDN?')
	if "33120" in fg.read():
		isNot33120A = False
	else:
		isNot33120A = True
	if isNot33120A:
		fg.write('FUNC SIN')
	else:
		fg.write('FUNC:SHAP SIN')
	fg.write(f'FREQ {limits_frequency[0]}')
	fg.write('VOLT:UNIT VPP')
	if isNot33120A:
		fg.write(f'VOLT {voltage_in/2}')
	else:
		fg.write(f'VOLT {voltage_in}')
	fg.write('VOLT:OFFS 0')
	fg.write('OUTP:LOAD INF')
	subplot_gain.set_xlim(limits_frequency)
	subplot_phase.set_xlim(limits_frequency)
	plot_canvas.draw()
	if isNot33120A:
		fg.write('OUTP ON')

def SetupScope(scope, voltage_in, voltage_out, channel_in, channel_out, freq, bw_in, bw_out, avg):
	scope.write('CLE')
	scope.write('RUN')
	scope.write('CHAN1:DISP OFF')
	scope.write('CHAN2:DISP OFF')
	scope.write('CHAN3:DISP OFF')
	scope.write('CHAN4:DISP OFF')
	scope.write(f'CHAN{channel_in}:DISP ON')
	scope.write(f'CHAN{channel_out}:DISP ON')
	scope.write(f'CHAN{channel_in}:BWL {bw_in}')
	scope.write(f'CHAN{channel_out}:BWL {bw_out}')
	scope.write(f'CHAN{channel_in}:COUP DC')
	scope.write(f'CHAN{channel_out}:COUP DC')
	scope.write(f'CHAN{channel_in}:INV OFF')
	scope.write(f'CHAN{channel_out}:INV OFF')
	scope.write(f'CHAN{channel_in}:OFFS 0')
	scope.write(f'CHAN{channel_out}:OFFS 0')
	scope.write(f'CHAN{channel_in}:PROB 1')
	scope.write(f'CHAN{channel_out}:PROB 1')
	scope.write(f'CHAN{channel_in}:UNIT VOLT')
	scope.write(f'CHAN{channel_out}:UNIT VOLT')
	scope.write('TIM:DEL:ENAB OFF')
	scope.write('TIM:MAIN:OFFS 0')
	scope.write('TIM:MODE MAIN')
	scope.write('TRIG:MODE EDGE')
	scope.write('TRIG:COUP DC')
	scope.write('TRIG:SWE AUTO')
	scope.write('TRIG:HOLD 0.000000016')
	scope.write('TRIG:NREJ ON')
	scope.write(f'TRIG:EDG:SOUR CHAN{channel_in}')
	scope.write('TRIG:EDG:SLOP POS')
	scope.write('TRIG:EDG:LEV 0')
	if int(float(avg)) == 1:
		scope.write('ACQ:TYPE NORM')
	else:
		scope.write('ACQ:TYPE AVER')
		scope.write(f'ACQ:AVER {int(float(avg))}')
	scope.write('MEAS:CLE ALL')
	scope.write(f'MEAS:CHAN {channel_in}')
	scope.write(f'MEAS:CHAN {channel_out}')
	scope.write(f'MEAS:SET:PSA CHAN{channel_out}')
	scope.write(f'MEAS:SET:PSB CHAN{channel_in}')
	scope.write(f'MEAS:ITEM VPP,CHAN{channel_in}')
	scope.write(f'MEAS:ITEM VPP,CHAN{channel_out}')
	scope.write(f'MEAS:ITEM FREQ,CHAN{channel_in}')
	scope.write(f'MEAS:ITEM FREQ,CHAN{channel_out}')
	scope.write('MEAS:ITEM RPH')
	UpdateScope(scope, voltage_in, voltage_out, channel_in, channel_out, freq)

def UpdateScope(scope, voltage_in, voltage_out, channel_in, channel_out, freq):
	scope.write(f'TIM:MAIN:SCAL {1/freq/6}')
	scope.write(f'CHAN{channel_in}:RANG {voltage_in * 2}')
	scope.write(f'CHAN{channel_out}:RANG {voltage_out * 2}')

def FunctionDisplayScale(val):
	global label_average2
	label_text = ""
	label_text = f"{2 ** int(float(val))} samples"
	if int(float(val)) == 0:
		label_text = "no averaging"
	label_average2.config(text=label_text)

def FunctionStop():
	global is_running
	try:
		fg.write('OUTP OFF')
		fg.close()
	except:
		pass
	try:
		scope.close()
	except:
		pass
	is_running = False
	button_update.configure(text="Start", command=FunctionUpdate, bg=color_start)

	try:
        	main_window.after_cancel(next_task)
	except:
		pass
	FunctionFinalizePlotLimits()

def FunctionCalculateDelay(ideal, avg, freq):
	return int(max(2000/freq*avg, ideal))

def FunctionUpdate():
	avg = 2 ** int(float(scale_average.get()))
	channel_in = combobox_channel_in.get()
	channel_out = combobox_channel_out.get()
	
	if channel_in == channel_out:
		tkinter.messagebox.showerror(title="Error", message="The input and output channels cannot be the same!")
		return
	
	nc_scope = True
	nc_fg = True
	scope = visa.Resource(rm, "")
	fg = visa.Resource(rm, "")
	try:
		scope = rm.open_resource(combobox_scope.get())
	except:
		scope.close()
		nc_scope = tkinter.messagebox.askyesno(title="Error", message=f"Could not connect to oscilloscope! Error: {sys.exc_info()}\n\nDo you wish to run the demo instead?")
		if not nc_scope:
			return
	else:
		nc_scope = False
		try:
			fg = rm.open_resource(combobox_fg.get())
		except:
			scope.close()
			fg.close()
			nc_fg = tkinter.messagebox.askyesno(title="Error", message=f"Couldn't connect to function generator! Error: {sys.exc_info()}\n\nDo you wish to run the demo instead?")
			if not nc_fg:
				return
		else:
			nc_fg = False
	
	dict_unit_frequency = {"mHz" : 0.001, "Hz" : 1, "kHz" : 1000, "MHz" : 1000000}
	setting_min = float(entry_frequency_min.get()) * dict_unit_frequency[combobox_unit_frequency_min.get()]
	memory_min = setting_min
	setting_max = float(entry_frequency_max.get()) * dict_unit_frequency[combobox_unit_frequency_max.get()]
	memory_max = setting_max
	if len(memory_list) < 0:
		for i in range(int(len(memory_list) / 3)):
			memory_min = min(memory_min, min(memory_list[i * 3]))
			memory_max = max(memory_max, max(memory_list[i * 3]))
	limits_frequency[0] = memory_min
	limits_frequency[1] = memory_max
	points = int(entry_points.get())
	
	dict_unit_voltage = {"mV" : 0.001, "V" : 1, "kV" : 1000}
	voltage_in = float(entry_voltage.get()) * dict_unit_voltage[combobox_unit_voltage.get()]
	voltage_out = voltage_in
	
	if limits_frequency[0] == limits_frequency[1]:
		tkinter.messagebox.showerror(title="Error", message="Lower and upper limit cannot be equal!")
		return
	elif points == 0:
		tkinter.messagebox.showerror(title="Error", message="At least one point per decade is necessary!")
	elif limits_frequency[0] > limits_frequency[1]:
		tkinter.messagebox.showwarning(title="Warning", message="The specified limits have been swapped, so that the lower limit is really lower than the upper limit.")
		temp = limits_frequency[0]
		limits_frequency[0] = limits_frequency[1]
		limits_frequency[1] = temp
		entry_frequency_min.delete(0, END)
		entry_frequency_min.insert(END, f"{limits_frequency[0]}")
		combobox_unit_frequency_min.set("Hz")
		entry_frequency_max.delete(0, END)
		entry_frequency_max.insert(END, f"{limits_frequency[1]}")
		combobox_unit_frequency_max.set("Hz")
	
	if limits_frequency[0] < 1:
		tkinter.messagebox.showwarning(title="Warning", message="The specified minimum was too small, so it was replaced with 1 Hz.")
		limits_frequency[0] = 1
		entry_frequency_min.delete(0, END)
		entry_frequency_min.insert(END, "1")
		combobox_unit_frequency_min.set("Hz")
	
	if limits_frequency[1] > 20000000:
		tkinter.messagebox.showwarning(title="Warning", message="The specified maximum was too high, so it was replaced with 20 MHz.")
		limits_frequency[1] = 20000000
		entry_frequency_max.delete(0, END)
		entry_frequency_max.insert(END, "20")
		combobox_unit_frequency_max.set("MHz")
	
	button_update.configure(text="Stop", command=FunctionStop, bg="red")
	global is_running
	is_running = True
	
	tens = 0
	while limits_frequency[0] < 1:
		limits_frequency[0] = limits_frequency[0] * 10
		limits_frequency[1] = limits_frequency[1] * 10
		tens = tens + 1
	
	step_set = FunctionFrequencySet(boolean_var_integers.get(), points)
	
	if len(step_set) < points and boolean_var_integers.get():
		tkinter.messagebox.showwarning(title="Warning", message="Not enough steps could be made with round frequencies, so no rounding was performed.")
		step_set = FunctionFrequencySet(not boolean_var_integers.get(), points)
	
	freq_set = set()
	frequency_current = limits_frequency[0]
	freq_set.add(limits_frequency[0])
	
	while frequency_current < limits_frequency[1]:
		for i in step_set:
			if frequency_current * i > limits_frequency[1]:
				break
			
			freq_set.add(round(frequency_current * i, 4))
		
		frequency_current = frequency_current * 10
	
	freq_set.add(limits_frequency[1])
	
	global freq_list
	freq_list = sorted(freq_set)
	
	while tens > 0:
		for i in range(0, len(freq_list)):
			freq_list[i] = round(freq_list[i] / 10, 10)
		tens = tens - 1
	
	if nc_fg or nc_scope:
		next_task = main_window.after(FunctionCalculateDelay(1000, avg, freq_list[0]), FunctionDemo, freq_list[0], 0, avg)
	else:
		dict_bool_to_on_off = {False: "OFF", True: "ON"}
		SetupFG(fg, voltage_in)
		SetupScope(scope, voltage_in, voltage_out, channel_in, channel_out, freq_list[0], dict_bool_to_on_off[boolean_var_bw_in.get()], dict_bool_to_on_off[boolean_var_bw_out.get()], avg)
		
		next_task = main_window.after(FunctionCalculateDelay(15000, avg, freq_list[0]), FunctionFrequencyChange, freq_list[0], 0, fg, scope, channel_in, channel_out, avg)

pane_main = PanedWindow(main_window)
pane_main.pack(fill=BOTH,expand=1)
pane_side = PanedWindow(pane_main,orient=VERTICAL)
pane_main.add(pane_side)
frame_device = Frame(pane_side)
pane_side.add(frame_device)
frame_device.pack(pady=10)
frame_measurement = Frame(pane_side)
pane_side.add(frame_measurement)
frame_measurement.pack(pady=10)
frame_data = Frame(pane_side)
pane_side.add(frame_data)
frame_data.pack(pady=10)
frame_plot = Frame(pane_main)
pane_main.add(frame_plot)

figure_bode = Figure(figsize=(5,6), dpi=100)
figure_bode.subplots_adjust(hspace=0.5)
subplot_gain = figure_bode.add_subplot(211)
subplot_phase = figure_bode.add_subplot(212)
FunctionInitBode()
plot_canvas = FigureCanvasTkAgg(figure_bode, master=frame_plot)
plot_canvas.get_default_filename = lambda: './measurementimage.png'
plot_canvas.draw()
plot_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
plot_toolbar = NavigationToolbar2Tk(plot_canvas, frame_plot)
plot_toolbar.update()

label_setup = Label(frame_device, text="Measurement setup", font=("Helvetica", 20))

label_fg = Label(frame_device, text="Function generator:", width=17, anchor="w")
combobox_fg = ttk.Combobox(frame_device, state="readonly", width=25, values=device_list)

label_scope = Label(frame_device, text="Oscilloscope:", width=17, anchor="w")
combobox_scope = ttk.Combobox(frame_device, state="readonly", width=25, values=device_list)

ListResources()

label_channel_in = Label(frame_device, text="Oscilloscope input channel:", width=32, anchor="w")
combobox_channel_in = ttk.Combobox(frame_device, state="readonly", values=[1, 2, 3, 4])
combobox_channel_in.config(width=1)
combobox_channel_in.set(1)
label_channel_out = Label(frame_device, text="Oscilloscope output channel:", width=32, anchor="w")
combobox_channel_out = ttk.Combobox(frame_device, state="readonly", values=[1, 2, 3, 4])
combobox_channel_out.config(width=1)
combobox_channel_out.set(2)
boolean_var_bw_in = BooleanVar()
boolean_var_bw_in.set(False)
checkbutton_bw_in = Checkbutton(frame_device, variable=boolean_var_bw_in, text="Oscilloscope bandwidth limit (input)", anchor="w")
boolean_var_bw_out = BooleanVar()
boolean_var_bw_out.set(False)
checkbutton_bw_out = Checkbutton(frame_device, variable=boolean_var_bw_out, text="Oscilloscope bandwidth limit (output)", anchor="w")
int_var_average = IntVar()
label_average1 = Label(frame_device, text="Taking average of")
label_average2 = Label(frame_device, text="no averaging", width=12, anchor="w")
scale_average = ttk.Scale(frame_device, orient=HORIZONTAL, length=100, from_=0, to=10, variable=int_var_average, command=FunctionDisplayScale)
scale_average.set(0)

button_refresh = Button(frame_device, text="Refresh", command=ListResources)

#frame_device.grid_rowconfigure((0, 10, 15, 17, 20, 30, 40, 50, 60), weight=1)
#frame_device.grid_columnconfigure((0, 10, 20, 25), weight=1)

label_setup.grid(row=0, column=0, columnspan=30, pady=20, sticky=EW)

label_fg.grid(row=10, column=0, padx=5, sticky=E)
combobox_fg.grid(row=10, column=10, columnspan=20, sticky=W)

label_scope.grid(row=15, column=0, padx=5, sticky=E)
combobox_scope.grid(row=15, column=10, columnspan=20, sticky=W)

checkbutton_bw_in.grid(row=40, column=0, padx=5, columnspan=30, sticky=EW)
checkbutton_bw_out.grid(row=50, column=0, padx=5, columnspan=30, sticky=EW)
label_average1.grid(row=60, column=0, padx=5, sticky=E)
scale_average.grid(row=60, column=10, padx=5, sticky=EW)
label_average2.grid(row=60, column=20, columnspan=10, padx=5, sticky=W)

button_refresh.grid(row=17, column=10, columnspan=20, pady=5, sticky=EW)

label_channel_in.grid(row=20, column=0, columnspan=25, padx=5, sticky=W)
combobox_channel_in.grid(row=20, column=25, sticky=E)
label_channel_out.grid(row=30, column=0, columnspan=25, padx=5, sticky=W)
combobox_channel_out.grid(row=30, column=25, sticky=E)


button_update=Button(frame_measurement, text="Start", command=FunctionUpdate)
button_update.config(width=10)
color_start = button_update.cget("background")

label_frequency=Label(frame_measurement, text="Frequency:")
set_of_frequency_measurement_units = ["Hz", "kHz", "MHz"]
entry_frequency_min=Entry(frame_measurement)
entry_frequency_min.config(width=5)
entry_frequency_min.insert(END, "20")
combobox_unit_frequency_min = ttk.Combobox(frame_measurement, state="readonly", values=set_of_frequency_measurement_units)
combobox_unit_frequency_min.config(width=4)
combobox_unit_frequency_min.set("Hz")
label_frequency_to = Label(frame_measurement, text="to")
entry_frequency_max=Entry(frame_measurement)
entry_frequency_max.config(width=5)
entry_frequency_max.insert(END, "20")
combobox_unit_frequency_max = ttk.Combobox(frame_measurement, state="readonly", values=set_of_frequency_measurement_units)
combobox_unit_frequency_max.set("kHz")
combobox_unit_frequency_max.config(width=4)

label_voltage=Label(frame_measurement, text="Voltage:")
entry_voltage=Entry(frame_measurement)
entry_voltage.config(width=5)
entry_voltage.insert(END, "1")
set_of_voltage_measurement_units = ["V"]
combobox_unit_voltage = ttk.Combobox(frame_measurement, state="readonly", values=set_of_voltage_measurement_units)
combobox_unit_voltage.set("V")
combobox_unit_voltage.config(width=4)
label_points = Label(frame_measurement, text="Points/decade:")
entry_points = Entry(frame_measurement)
entry_points.config(width=5)
entry_points.insert(END, "3")
boolean_var_integers = BooleanVar()
boolean_var_integers.set(True)
checkbutton_float = Checkbutton(frame_measurement, variable=boolean_var_integers, text="Round values")


button_update.grid(row=30, column=0, columnspan=50)

label_frequency.grid(row=0, column=0)
entry_frequency_min.grid(row=0, column=10)
combobox_unit_frequency_min.grid(row=0, column=20)
label_frequency_to.grid(row=0, column=25, padx=10)
entry_frequency_max.grid(row=0, column=30)
combobox_unit_frequency_max.grid(row=0, column=40)

label_points.grid(row=10, column=0, columnspan=20, sticky="w")
entry_points.grid(row=10, column=20)
checkbutton_float.grid(row=10, column=25, columnspan=25)

label_voltage.grid(row=20, column=0, sticky="w", pady=20)
entry_voltage.grid(row=20, column=10)
combobox_unit_voltage.grid(row=20, column=20)


checkbutton_db = Checkbutton(frame_data, variable=boolean_var_gain_in_db, text="Gain in decibels", command=FunctionUpdateGain)
checkbutton_rad = Checkbutton(frame_data, variable=boolean_var_phase_in_radians, text="Phase difference in radians", command=FunctionUpdatePhaseDifference)
button_clear = Button(frame_data, text="Clear previous figures", command=FunctionClearFigure)

button_export = Button(frame_data, text="Export .csv", command=FunctionExport)
button_import = Button(frame_data, text="Import .csv", command=FunctionImport)


checkbutton_db.pack()
checkbutton_rad.pack()
button_clear.pack(pady=10)
button_import.pack(fill="both", side=LEFT)
button_export.pack(fill="both", side=RIGHT)


main_window.mainloop()

MyActiveLowPass
The MyActiveLowPass component should filter out all input voltages with a frequency higher than the given input parameter cutoff frequency (named "fc") It should allow all input voltage signals with a frequency lower than fc to pass through, amplified by a factor of 2. The output impedence of the component should be extremely high to prevent loading effects. The component's public interface should have exactly 3 pins: 1. a positive pin named "pin_p" where the input signal should be attached; 2. a negative pin named "pin_n" where the ground should be attached; and 3. a pin named "Vout" where the filtered signal can be found. Do not use a ground in your definition.

model LowPassTest
  Modelica.Electrical.Analog.Sources.SineVoltage high_freq(V = 12, f = 10)  annotation(
    Placement(visible = true, transformation(origin = {-52, 10}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Modelica.Electrical.Analog.Sources.SineVoltage low_freq(V = 12, f = 0.1)  annotation(
    Placement(visible = true, transformation(origin = {-52, -20}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Modelica.Electrical.Analog.Basic.Ground GND annotation(
    Placement(visible = true, transformation(origin = {0, -48}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  MyActiveLowPass LP(fc = 1)  annotation(
    Placement(visible = true, transformation(origin = {0, 18}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
equation
  connect(low_freq.n, GND.p) annotation(
    Line(points = {{-52, -30}, {-52, -38}, {0, -38}}, color = {0, 0, 255}));
  connect(high_freq.n, low_freq.p) annotation(
    Line(points = {{-52, 0}, {-52, -10}}, color = {0, 0, 255}));
  connect(high_freq.p, LP.pin_p) annotation(
    Line(points = {{-52, 20}, {-29, 20}, {-29, 19}, {-9, 19}}, color = {0, 0, 255}));
  connect(LP.pin_n, GND.p) annotation(
    Line(points = {{0, 14}, {0, -38}}, color = {0, 0, 255}));
  annotation(
    uses(Modelica(version = "4.0.0")),
  Diagram(coordinateSystem(extent = {{-60, 20}, {20, -60}})),
  version = "");
end LowPassTest;

simulate(LowPassTest, stopTime=10); plot({high_freq.v, low_freq.v, LP.Vout.v})

MyLowPass
The LowPass component should filter out all input voltages with a frequency higher than the given breakpoint frequency. It should allow all input voltages with a frequency lower than the given breakpoint frequency to pass through. The filtered signal should be available at the output pin (named "Vout"). Interface: LowPass should accept a voltage signal input at LowPass.p, a GND at LowPass.n, and the output (filtered) voltage should be found at LowPass.Vout.v.

model LowPassTest
  MyLowPass high_freq(breakpoint=1e2);
  MyLowPass low_freq(breakpoint=1e2);
  Modelica.Electrical.Analog.Sources.SineVoltage V1(V=12, f=1e3);
  Modelica.Electrical.Analog.Sources.SineVoltage V2(V=12, f=1e1);
  Modelica.Electrical.Analog.Basic.Ground GND;
equation
  connect(V1.p, high_freq.p);
  connect(high_freq.n, GND.p);
  connect(V1.n, GND.p);

  connect(V2.p, low_freq.p);
  connect(low_freq.n, GND.p);
  connect(V2.n, GND.p);
end LowPassTest;

simulate(LowPassTest, stopTime=1); plot({high_freq.Vout.v, low_freq.Vout.v});

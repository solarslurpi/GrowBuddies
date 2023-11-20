load("math.star", "math")

def saturation_vapor_pressure(temp_celsius):
#  return 0.6108 * math.exp((17.27 * temp_celsius) / (temp_celsius + 237.3))
   #x = (17.27 * temp_celsius) / (temp_celsius + 237.3)
   #exp_x = 1 + x + (x**2)/2 + (x**3)/6 + (x**4)/24 + (x**5)/120  # Including up to the x^4 term for illustration
   # Apply the expansion to the original expression
   #result = 0.6108 * exp_x   

   result = 0.6108 * math.exp((17.27 * temp_celsius) / (temp_celsius + 237.3))

   return result

def calculate_vpd(temp_celsius,humidity):
   air_T = temp_celsius
   leaf_T = air_T -2
   svp_air = saturation_vapor_pressure(air_T)
   svp_leaf = saturation_vapor_pressure(leaf_T)
   actual_air = humidity*svp_air/100
   return svp_leaf - actual_air

def apply(metric):  
  air_T = metric.fields['temperature']
  humidity = metric.fields['humidity']
  metric.fields['vpd'] = calculate_vpd(air_T, humidity)
  photo_resistor = metric.fields['light']
  if photo_resistor > 999:
    metric.fields['light'] = 1
  else:
    metric.fields['light'] = 0
  # Finally, set temp to F..sigh..
  metric.fields['temperature'] = (air_T * 9/5) + 32
  return metric

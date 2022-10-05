*****************
GrowBuddy Service
*****************
The GrowBuddy Service is a `Systemd <https://en.wikipedia.org/wiki/Systemd>`_ service written in Python running an a Raspberry Pi (3 or 4).  GrowBuddy is a Parent class providing back end services such as:

.. - logging for debugging and auditing. See :meth:`~FHmonitor.monitor.Monitor.take_reading
- handling of mqtt messages.
- writing readings to an InfluxDB measurement (which is what Influx seems to call a Table within a database).
  
 to the GrowBuddy sensors (like :ref:`SnifferBuddy`).

.. automodule:: growbuddy
    :members:
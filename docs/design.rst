The design of accml and accml\_lib
==================================

The design of `accml` and `accml_lib`is based on the following
observations:

* Different components of the full software stack have
  different views of the same "reality".
* We need to execute measurements, analyse them, store and
  exchange measurement results and so on: here a structured
  communication comes to our help.
* Many measurements are done "relative" to the current state.
  So we want to explore the current teritory.

Handling views
--------------

* particle accelerators are simulated by tools that calculate
  the difference to an ideal orbit or to be more precise a
  real world particle with respect to the movement of an
  ideal particle in an idealised accelerator
* in the real world however we need to deal with particles, their
  position and behavior in the real world.

We address this reality by the concept of `views`: both calculations
and operating the real world particle accelerator have the same
target: provide a machine with best possible performance. But they
see or view the same thing from a different angle.

These views have to be combined. Therefore, we need to take care
that the actual situation the system is in is as much the same as
possible in both views: actually we need to take care to connect
them and keep them on the same state: so simple snippets of
information need to be exchanged between the two.
Furthermore, we need to realise that the building blocks of the
simulation and the real world devices do not match exactly to each
other: they do often but not always and even then they need different
values.

The problem is tackled by:

    * each message of them needs an "building block" identifier and
      and a property identifier. Like business letters would be
      addressed to a person and contain a sign. Now note that
      the letters typically contain a "your sign", "our-sign.

      Here the liaison manager comes it: in large collaboration
      these people connect the participants: whom to talk to for
      certain types of problems to get it solved.

      The same concept applies here, but it needs to be structured
      so that simple computer programs can handle it.

    * the values need to be translated between the different views.
      Same in an internationally collaboration not all speak the
      same language. So you need a translation service to get communiques
      or letters translated. The same applies here. A translation service
      will provide you a translation service given that you know the
      parameters.

A general overview of these views is given in :cite:`accml:icaleps2025`.
The patterns mentiond above are explained in detail in :cite:`dt:europlop25`.


Structured communication
------------------------

We need to update values of the simulation engine or the real
machine, execute measurements or analyse them. So communications
are based on commands:

* its simplest is the "ReadCommand":

  .. code-block:: python

    ReadCommand(id="quad", property="set_current")

  We express that we want to read something. The command is then
  handled over to the appropriate backend. Details on that will
  be given later.

* for changing a value we use a "Command":

  .. code-block:: python

    Command(id="quad", property="set_current", value="245", behaviour_on_error=None)

  Here we formulate that the quadrupole current will be set to 245 Ampere.
  What shall happen in case of an error we leave undefined.


A general overview is given in :cite:`accml:icaleps2025`.
The patterns mentioned above are explained in detail in :cite:`dt:europlop25`.

Out of these building blocks we can build a whole structured communication. Instead
of specifying detectors we just specify what should be read. Based on commands we
build:

* transaction commands: these shall be executed at the same time
* a command sequence: these (transaction) commands shall be executed step by step.

A command execution engine takes care to execute these commands. A measurement execution
engine -- an enrichment of a command execution engine -- will additionally hand over
produced data to a storage.


Build up of the command engine
------------------------------



.. rubric:: References

.. bibliography:: refs.bib
   :style: unsrt
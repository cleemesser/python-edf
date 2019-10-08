This package contains 4 files in European Data Format (EDF). This format is
described at www.hsr.nl/edf. The corresponding gif's show a screenshot made by
our EDF viewer Polyman.

The files calib.rec and edffile.rec with their gif's help to check the
calibration of amplitude (including polarity) and time of your EDF viewer.

The file PositiveSpikes.edf (made by Jesus Olivan) contains a signal of +1uV
positive spikes on a 0uV baseline. The corresponding gif illustrates how a viewer
can show these spikes either upward or downward, by simply changing the
calibration of the display (left pane). The top pane has positive signals upward
while the bottom pane has positive signals downward.

The file K-complex.rec and its gif illustrate how the "negative-up" rule in
Clinical Neurophysiology can be applied by such a viewer. The file contains a
typical K-complex. The K-comples occurs at Cz, has a small positive wave,
followed by a large and sharp negative wave which is followed by a small positive
wave. A sleep spindle is superimposed on top of the last positive wave. The sharp
wave is negative on Cz, so it is positive in the signal Fpz-Cz which is in the
EDF file.

The top pane in K-complex.gif shows Fpz-Cz in a range from -250uV (bottom) to
+250uV (top). Because the sharp wave is negative at Cz, it is positive in Fpz-Cz
and it is displayed upward.

This viewer can also construct the inverted signal, Cz-Fpz. The middle pane shows
the inverted signal, Cz-Fpz, in the same amplitude range. The negative sharp wave
at Cz is also negative in Cz-Fpz and drawn downward.

The bottom pane shows the inverted signal, Cz-Fpz, in an inverted range from
+250uV (bottom) to -250uV (top). The negative transient in Cz is of course still
a negative transient in Cz-Fpz but now displayed upward because the viewer has
inverted its display.

Bob Kemp

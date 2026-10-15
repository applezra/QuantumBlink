namespace QuantumBlink
{
    // What happened this frame, so the mod can log it.
    public enum BlinkEvent
    {
        None,
        BlinkStarted,      // a blink now counts in the game
        BlinkEnded,        // the eyes opened after a counted blink
        ShortBlinkIgnored  // Intentional mode: the eyes opened before the hold time
    }

    // Turns the raw "are the eyes closed right now?" signal into game blinks.
    // Real-time mode: every closure counts immediately.
    // Intentional mode: the eyes must stay closed for HoldTime seconds first.
    public class BlinkFilter
    {
        public bool IntentionalMode;
        public float HoldTime = 0.6f;

        public bool IsBlinking { get; private set; }
        public float LastClosureLength { get; private set; }

        // True as soon as the eyes close, even before a blink counts (useful for showing "keep holding").
        public bool EyesClosed => eyesClosed;

        private bool eyesClosed;
        private float closedSince;

        // Call once per frame with the latest eye state and the current time in seconds.
        public BlinkEvent Update(bool eyesClosedNow, float time)
        {
            if (eyesClosedNow && !eyesClosed)
            {
                // The eyes just closed: start timing.
                eyesClosed = true;
                closedSince = time;
            }
            else if (!eyesClosedNow && eyesClosed)
            {
                // The eyes just opened.
                eyesClosed = false;
                LastClosureLength = time - closedSince;

                if (IsBlinking)
                {
                    IsBlinking = false;
                    return BlinkEvent.BlinkEnded;
                }
                return BlinkEvent.ShortBlinkIgnored;
            }

            // Have the eyes been closed long enough? In Real-time mode there's no wait at all.
            if (eyesClosed && !IsBlinking)
            {
                float needed = IntentionalMode ? HoldTime : 0f;
                if (time - closedSince >= needed)
                {
                    IsBlinking = true;
                    return BlinkEvent.BlinkStarted;
                }
            }

            return BlinkEvent.None;
        }

        // How far the current eye closure is through the hold time: 0 = eyes open, 1 = the blink counts.
        // In Real-time mode a closure counts straight away, so it jumps from 0 to 1.
        public float HoldProgress(float time)
        {
            if (IsBlinking) return 1f;
            if (!eyesClosed || HoldTime <= 0f) return 0f;
            return System.Math.Min(1f, (time - closedSince) / HoldTime);
        }

        // Forget everything, as if the eyes were open.
        public void Reset()
        {
            eyesClosed = false;
            IsBlinking = false;
        }
    }
}

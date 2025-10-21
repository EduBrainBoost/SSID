import React from "react";

type Props = {
  userOverride: boolean;
  setUserOverride: (v: boolean) => void;
};

export default function RewardPreferenceToggle({ userOverride, setUserOverride }: Props) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-2xl shadow">
      <label className="text-sm">Alles in Geld auszahlen (Eigenverantwortung)</label>
      <input
        type="checkbox"
        checked={userOverride}
        onChange={(e) => setUserOverride(e.target.checked)}
      />
    </div>
  );
}

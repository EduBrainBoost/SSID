
import React from "react";

export function RegionToggle({ zones, selected, onChange }:{ zones:any, selected:string[], onChange:(v:string[])=>void }){
  const zoneKeys = Object.keys(zones || {});
  return (
    <div>
      <h3 className="font-semibold">Regionen</h3>
      <div className="flex flex-wrap gap-2">
        {zoneKeys.map((k) => (
          <label key={k} className="flex items-center gap-2 border rounded-lg px-2 py-1">
            <input
              type="checkbox"
              checked={selected.includes(k)}
              onChange={(e) => {
                const checked = e.target.checked;
                onChange(checked ? Array.from(new Set([...selected, k])) : selected.filter((x) => x !== k));
              }}
            />
            <span>{k}</span>
          </label>
        ))}
      </div>
    </div>
  )
}

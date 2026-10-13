/* Deterministic TOF classification; see 2023 ASA practice guideline.
   The browser app provides education, not treatment decisions. */
export function interpretTOF({count, ptc = null, ratio = null}) {
  if (!Number.isInteger(count) || count < 0 || count > 4) {
    throw new RangeError("TOF count must be an integer from 0 to 4.");
  }
  if (ptc !== null) {
    if (!Number.isInteger(ptc) || ptc < 0 || ptc > 30) {
      throw new RangeError("PTC must be an integer from 0 to 30.");
    }
    if (count !== 0) throw new RangeError("PTC applies only when TOF count is zero.");
  }
  if (ratio !== null) {
    if (typeof ratio !== "number" || !Number.isFinite(ratio) || ratio < 0 || ratio > 1.5) {
      throw new RangeError("TOF ratio must be a finite number from 0 to 1.5.");
    }
    if (count !== 4) throw new RangeError("A TOF ratio requires four detected twitches.");
  }
  let category, detail;
  if (count === 0 && ptc === null) {
    category = "INDETERMINATE";
    detail = "No TOF response; PTC is needed to distinguish complete from deep block.";
  } else if (count === 0 && ptc === 0) {
    category = "COMPLETE";
    detail = "No TOF twitch or post-tetanic response was observed.";
  } else if (count === 0) {
    category = "DEEP";
    detail = "No TOF twitch; at least one post-tetanic response was observed.";
  } else if (count < 4) {
    category = "MODERATE";
    detail = count + " of 4 twitches were observed.";
  } else if (ratio === null) {
    category = "INDETERMINATE";
    detail = "Four twitches were detected, but quantitative TOF ratio was not supplied.";
  } else if (ratio < 0.4) {
    category = "SHALLOW";
    detail = "Four twitches with quantitative TOF ratio below 0.4.";
  } else if (ratio < 0.9) {
    category = "MINIMAL";
    detail = "Four twitches with quantitative TOF ratio from 0.4 to below 0.9.";
  } else {
    category = "RECOVERED";
    detail = "Measured TOF ratio is at least 0.9. Other clinical criteria still apply.";
  }
  return {
    category, detail, recovery_threshold_met: category === "RECOVERED",
    note: "Educational interpretation only; not for dosing or extubation decisions.",
    source: "2023 ASA practice guidelines; DOI:10.1097/ALN.0000000000004379"
  };
}

if (typeof document !== "undefined") {
  const form = document.getElementById("tof-form");
  const countElement = document.getElementById("count");
  const ptcElement = document.getElementById("ptc");
  const ratioElement = document.getElementById("ratio");
  const ptcField = document.getElementById("ptc-field");
  const ratioField = document.getElementById("ratio-field");
  const errorElement = document.getElementById("errors");
  const resultElement = document.getElementById("result");
  const categoryElement = document.getElementById("category");
  const detailElement = document.getElementById("detail");
  const exportButton = document.getElementById("export");
  let lastExport = null;

  const updateControls = () => {
    const count = Number(countElement.value);
    ptcField.hidden = count !== 0;
    ratioField.hidden = count !== 4;
    ptcElement.disabled = count !== 0;
    ratioElement.disabled = count !== 4;
    if (count !== 0) ptcElement.value = "";
    if (count !== 4) ratioElement.value = "";
    errorElement.textContent = "";
    exportButton.disabled = true;
    lastExport = null;
    resultElement.removeAttribute("data-level");
    categoryElement.textContent = "Not evaluated";
    detailElement.textContent = "Select “Interpret observation” to classify these measurements.";
  };
  countElement.addEventListener("change", updateControls);
  updateControls();

  form.addEventListener("submit", event => {
    event.preventDefault();
    errorElement.textContent = "";
    try {
      const count = Number(countElement.value);
      const ptc = count === 0 && ptcElement.value.trim() !== "" ? Number(ptcElement.value) : null;
      const ratio = count === 4 && ratioElement.value.trim() !== "" ? Number(ratioElement.value) : null;
      const interpretation = interpretTOF({count, ptc, ratio});
      categoryElement.textContent = interpretation.category;
      detailElement.textContent = interpretation.detail;
      resultElement.dataset.level = interpretation.category;
      lastExport = {observations: {tof_count: count, ptc, tof_ratio: ratio}, interpretation};
      exportButton.disabled = false;
    } catch (error) {
      lastExport = null;
      exportButton.disabled = true;
      resultElement.removeAttribute("data-level");
      categoryElement.textContent = "Invalid input";
      detailElement.textContent = "Correct the observations and try again.";
      errorElement.textContent = error.message;
    }
  });
  exportButton.addEventListener("click", () => {
    if (!lastExport) return;
    const blob = new Blob([JSON.stringify(lastExport, null, 2) + "\n"], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "tof-educational-interpretation.json";
    link.click();
    URL.revokeObjectURL(url);
  });
}

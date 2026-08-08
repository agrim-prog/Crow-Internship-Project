import { formatCurrency, isFieldFlagged } from "@/lib/format";
import { FIELD_META, GROUP_LABELS, type LeaseAbstract } from "@/lib/schema";

export default function PrintableAbstract({
  result,
  sourceLabel,
}: {
  result: LeaseAbstract;
  sourceLabel: string;
}) {
  const groups = Array.from(new Set(FIELD_META.map((f) => f.group)));

  return (
    <div className="hidden print:block">
      <h1 className="text-2xl font-semibold">Lease Abstract</h1>
      <p className="mt-1 text-sm text-neutral-600">
        {sourceLabel} · generated {new Date().toLocaleDateString()}
      </p>

      {groups.map((group) => (
        <div key={group} className="mt-6">
          <h2 className="border-b border-black/20 pb-1 text-xs font-medium uppercase tracking-[0.1em]">
            {GROUP_LABELS[group]}
          </h2>
          <table className="mt-2 w-full text-sm">
            <tbody>
              {FIELD_META.filter((f) => f.group === group).map((field) => {
                const value = result[field.key];
                const missing = value === null || value === undefined;
                const flagged = isFieldFlagged(result, field.key);
                const display = missing
                  ? "Not found in document"
                  : field.key === "monthly_rent"
                  ? formatCurrency(value as number)
                  : String(value);
                return (
                  <tr key={field.key}>
                    <td className="w-40 py-1 pr-4 align-top text-xs font-medium uppercase tracking-[0.06em] text-neutral-600">
                      {field.label}
                    </td>
                    <td className="py-1 align-top">
                      {display}
                      {flagged && !missing ? " (needs review)" : ""}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ))}

      {result.key_provisions?.length ? (
        <div className="mt-6">
          <h2 className="border-b border-black/20 pb-1 text-xs font-medium uppercase tracking-[0.1em]">
            Key provisions
          </h2>
          <ul className="mt-2 list-disc pl-5 text-sm">
            {result.key_provisions.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {result.uncertainty_notes ? (
        <div className="mt-6">
          <h2 className="border-b border-black/20 pb-1 text-xs font-medium uppercase tracking-[0.1em]">
            Notes
          </h2>
          <p className="mt-2 text-sm">{result.uncertainty_notes}</p>
        </div>
      ) : null}
    </div>
  );
}

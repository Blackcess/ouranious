import { useCallback, useEffect, useRef, useState } from "react";
import { enums, provenanceApi } from "../../../api/provenance/provenanceApi";
import { getErrorMessage } from "../../../api/provenance/errors";
import ClaimLookup from "./claim-review/ClaimLookup";
import ClaimDetails from "./claim-review/ClaimDetails";
import ClaimSources from "./claim-review/ClaimSources";
import ClaimStatusPanel from "./claim-review/ClaimStatusPanel";
import AssessmentPanel from "./claim-review/AssessmentPanel";
import AssessmentHistory from "./claim-review/AssessmentHistory";
import MaterialisationPanel from "./claim-review/MaterialisationPanel";

const initialAssessmentForm = {
  outcome: "accept",
  rationale: "",
  assessed_by: "",
  review_process: "",
  transition_claim_to: "",
};

export default function ClaimReview({ initialClaimId, onClaimSelected }) {
  const [claimIdInput, setClaimIdInput] = useState(initialClaimId || "");
  const [claim, setClaim] = useState(null);
  const [claimLoading, setClaimLoading] = useState(false);
  const [claimError, setClaimError] = useState(null);
  const [sourceRecords, setSourceRecords] = useState({});
  const [sourcesLoading, setSourcesLoading] = useState(false);
  const [sourcesError, setSourcesError] = useState(null);
  const [assessments, setAssessments] = useState([]);
  const [assessmentsLoading, setAssessmentsLoading] = useState(false);
  const [assessmentsError, setAssessmentsError] = useState(null);
  const [materialisation, setMaterialisation] = useState(null);
  const [assessmentForm, setAssessmentForm] = useState(initialAssessmentForm);
  const [associationId, setAssociationId] = useState("");
  const [statusTarget, setStatusTarget] = useState("");
  const [allowDuplicate, setAllowDuplicate] = useState(false);
  const [associationLoading, setAssociationLoading] = useState(false);
  const [statusLoading, setStatusLoading] = useState(false);
  const [assessmentSubmitting, setAssessmentSubmitting] = useState(false);
  const [materialisationLoading, setMaterialisationLoading] = useState(false);
  const [notice, setNotice] = useState(null);
  const loadRequestId = useRef(0);
  const activeClaimId = useRef(null);
  const loadedClaimId = useRef(null);
  const routeClaimId = useRef(initialClaimId || null);

  const loadClaim = useCallback(async (claimId) => {
    const requestId = loadRequestId.current + 1;
    loadRequestId.current = requestId;
    activeClaimId.current = claimId;

    setClaim(null);
    setSourceRecords({});
    setAssessments([]);
    setMaterialisation(null);
    setAssociationId("");
    setStatusTarget("");
    setAssessmentForm(initialAssessmentForm);
    setAllowDuplicate(false);
    setClaimError(null);
    setSourcesError(null);
    setAssessmentsError(null);
    setNotice(null);
    setClaimLoading(true);
    setSourcesLoading(false);
    setAssessmentsLoading(false);

    try {
      const found = await provenanceApi.getClaim(claimId);
      if (requestId !== loadRequestId.current) return;

      loadedClaimId.current = found.id;
      setClaim(found);
      setClaimIdInput(found.id);
      onClaimSelected?.(found.id);
      setClaimLoading(false);
      setSourcesLoading(true);
      setAssessmentsLoading(true);

      const sourceRequest = Promise.all(found.source_ids.map(async (sourceId) => {
        try {
          return { sourceId, source: await provenanceApi.getSource(sourceId), error: null };
        } catch (error) {
          return { sourceId, source: null, error };
        }
      }));
      const assessmentsRequest = provenanceApi.getAssessments(found.id)
        .then((rows) => ({ rows, error: null }))
        .catch((error) => ({ rows: [], error }));
      const [sourceResults, historyResult] = await Promise.all([sourceRequest, assessmentsRequest]);

      if (requestId !== loadRequestId.current) return;

      setSourceRecords(Object.fromEntries(sourceResults.map(({ sourceId, source }) => [sourceId, source])));
      const sourceFailure = sourceResults.find(({ error }) => error)?.error;
      setSourcesError(sourceFailure ? getErrorMessage(sourceFailure) : null);
      setAssessments(historyResult.rows);
      setAssessmentsError(historyResult.error ? getErrorMessage(historyResult.error) : null);
    } catch (error) {
      if (requestId === loadRequestId.current) {
        setClaimError(getErrorMessage(error));
      }
    } finally {
      if (requestId === loadRequestId.current) {
        setClaimLoading(false);
        setSourcesLoading(false);
        setAssessmentsLoading(false);
      }
    }
  }, [onClaimSelected]);

  useEffect(() => {
    if (!initialClaimId) {
      if (routeClaimId.current) {
        routeClaimId.current = null;
        loadRequestId.current += 1;
        activeClaimId.current = null;
        loadedClaimId.current = null;
        setClaimIdInput("");
        setClaim(null);
        setClaimLoading(false);
        setClaimError(null);
        setSourceRecords({});
        setSourcesLoading(false);
        setSourcesError(null);
        setAssessments([]);
        setAssessmentsLoading(false);
        setAssessmentsError(null);
        setMaterialisation(null);
        setAssessmentForm(initialAssessmentForm);
        setAssociationId("");
        setStatusTarget("");
        setAllowDuplicate(false);
        setNotice(null);
      }
      return;
    }
    routeClaimId.current = initialClaimId;
    setClaimIdInput(initialClaimId);
    if (loadedClaimId.current === initialClaimId) return;
    loadClaim(initialClaimId);
  }, [initialClaimId, loadClaim]);

  const handleLookup = () => {
    const claimId = claimIdInput.trim();
    if (claimId) loadClaim(claimId);
  };

  const handleAssociationIdChange = (sourceId) => setAssociationId(sourceId);
  const handleAttachSource = (sourceId) => handleAssociation(sourceId, "attach");
  const handleRemoveSource = (sourceId) => handleAssociation(sourceId, "remove");
  const handleStatusTargetChange = (status) => setStatusTarget(status);
  const handleAssessmentFormChange = (field, value) => {
    setAssessmentForm((previous) => ({ ...previous, [field]: value }));
  };

  const handleAssociation = async (sourceId, action) => {
    if (!claim || associationLoading) return;
    const selectedClaimId = claim.id;
    const requestId = loadRequestId.current;
    setAssociationLoading(true);
    setNotice(null);

    try {
      if (action === "attach") {
        await provenanceApi.addSource(selectedClaimId, sourceId);
      } else {
        await provenanceApi.removeSource(selectedClaimId, sourceId);
      }
      if (activeClaimId.current !== selectedClaimId || requestId !== loadRequestId.current) return;
      setNotice({ kind: "success", text: action === "attach" ? "Source attached." : "Source detached." });
      await loadClaim(selectedClaimId);
    } catch (error) {
      if (activeClaimId.current === selectedClaimId && requestId === loadRequestId.current) {
        setNotice({ kind: "error", text: getErrorMessage(error) });
      }
    } finally {
      setAssociationLoading(false);
    }
  };

  const updateClaimStatus = async () => {
    if (!claim || !statusTarget || statusLoading) return;
    const selectedClaimId = claim.id;
    const requestId = loadRequestId.current;
    setStatusLoading(true);
    setNotice(null);

    try {
      const updatedClaim = await provenanceApi.updateClaimStatus(selectedClaimId, statusTarget);
      if (activeClaimId.current !== selectedClaimId || requestId !== loadRequestId.current) return;
      setClaim(updatedClaim);
      setStatusTarget("");
      setNotice({ kind: "success", text: "Claim status updated." });
    } catch (error) {
      if (activeClaimId.current === selectedClaimId && requestId === loadRequestId.current) {
        setNotice({ kind: "error", text: getErrorMessage(error) });
      }
    } finally {
      setStatusLoading(false);
    }
  };

  const createAssessment = async (event) => {
    event.preventDefault();
    if (!claim || assessmentSubmitting) return;
    const selectedClaimId = claim.id;
    const requestId = loadRequestId.current;
    setAssessmentSubmitting(true);
    setNotice(null);

    try {
      const created = await provenanceApi.createAssessment(selectedClaimId, {
        ...assessmentForm,
        transition_claim_to: assessmentForm.transition_claim_to || null,
        review_process: assessmentForm.review_process || null,
      });
      if (activeClaimId.current !== selectedClaimId || requestId !== loadRequestId.current) return;
      if (created.claim_status) {
        setClaim((previous) => ({ ...previous, status: created.claim_status }));
      }
      setAssessments((previous) => [created.assessment, ...previous]);
      setAssessmentForm(initialAssessmentForm);
      setNotice({ kind: "success", text: "Assessment recorded." });
    } catch (error) {
      if (activeClaimId.current === selectedClaimId && requestId === loadRequestId.current) {
        setNotice({ kind: "error", text: getErrorMessage(error) });
      }
    } finally {
      setAssessmentSubmitting(false);
    }
  };

  const refreshAssessments = async () => {
    if (!claim || assessmentsLoading) return;
    const selectedClaimId = claim.id;
    const requestId = loadRequestId.current;
    setAssessmentsLoading(true);
    setAssessmentsError(null);

    try {
      const rows = await provenanceApi.getAssessments(selectedClaimId);
      if (activeClaimId.current === selectedClaimId && requestId === loadRequestId.current) {
        setAssessments(rows);
      }
    } catch (error) {
      if (activeClaimId.current === selectedClaimId && requestId === loadRequestId.current) {
        setAssessmentsError(getErrorMessage(error));
      }
    } finally {
      if (activeClaimId.current === selectedClaimId && requestId === loadRequestId.current) {
        setAssessmentsLoading(false);
      }
    }
  };

  const handleMaterialise = async () => {
    if (!claim || materialisationLoading) return;
    const selectedClaimId = claim.id;
    const requestId = loadRequestId.current;
    setMaterialisationLoading(true);
    setNotice(null);

    try {
      const result = await provenanceApi.materialise(selectedClaimId, allowDuplicate);
      if (activeClaimId.current !== selectedClaimId || requestId !== loadRequestId.current) return;
      setMaterialisation(result.data);
      setNotice({
        kind: result.status === 409 ? "warning" : "success",
        text: result.status === 409
          ? "Resolution was blocked. Review the candidates and claim data."
          : `Materialisation response: HTTP ${result.status}.`,
      });
    } catch (error) {
      if (activeClaimId.current === selectedClaimId && requestId === loadRequestId.current) {
        setNotice({ kind: "error", text: getErrorMessage(error) });
      }
    } finally {
      setMaterialisationLoading(false);
    }
  };

  return (
    <section className="prov-review-layout">
      <ClaimLookup
        claimIdInput={claimIdInput}
        onClaimIdChange={(event) => setClaimIdInput(event.target.value)}
        onLookup={handleLookup}
        loading={claimLoading && claimIdInput.trim() === activeClaimId.current}
        disabled={!claimIdInput.trim() || (claimLoading && claimIdInput.trim() === activeClaimId.current)}
      />

      {claimError && <div className="prov-notice notice-error" role="alert">{claimError}</div>}
      {notice && <div className={`prov-notice notice-${notice.kind}`} role="status">{notice.text}</div>}

      {claim ? (
        <>
          <section className="prov-panel">
            <ClaimDetails claim={claim} />
            <ClaimSources
              claim={claim}
              sourceRecords={sourceRecords}
              sourcesLoading={sourcesLoading}
              sourcesError={sourcesError}
              associationId={associationId}
              associationLoading={associationLoading}
              onAssociationIdChange={handleAssociationIdChange}
              onAttachSource={handleAttachSource}
              onRemoveSource={handleRemoveSource}
            />
            <ClaimStatusPanel
              statusTarget={statusTarget}
              statusLoading={statusLoading}
              allowedTransitions={enums.allowedStatusTransitions[claim.status] || []}
              onStatusTargetChange={handleStatusTargetChange}
              onUpdateStatus={updateClaimStatus}
            />
          </section>

          <div className="prov-two-col">
            <AssessmentPanel
              claim={claim}
              assessmentForm={assessmentForm}
              assessmentSubmitting={assessmentSubmitting}
              onAssessmentFormChange={handleAssessmentFormChange}
              onSubmit={createAssessment}
            />

            <MaterialisationPanel
              allowDuplicate={allowDuplicate}
              materialisation={materialisation}
              materialisationLoading={materialisationLoading}
              onAllowDuplicateChange={setAllowDuplicate}
              onMaterialise={handleMaterialise}
            />
          </div>

          <AssessmentHistory
            assessments={assessments}
            assessmentsLoading={assessmentsLoading}
            assessmentsError={assessmentsError}
            onRefresh={refreshAssessments}
          />
        </>
      ) : (
        <div className="prov-empty">
          <span>◎</span>
          <h2>{claimLoading ? "Loading claim…" : "Start with a claim ID"}</h2>
          <p>Load a claim to inspect its evidence, assessment history, and materialisation state.</p>
        </div>
      )}
    </section>
  );
}

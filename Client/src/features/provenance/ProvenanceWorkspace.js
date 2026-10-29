import { useCallback, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate, useOutletContext, useParams } from "react-router-dom";
import ClaimCreator from "./components/ClaimCreator";
import ClaimReview from "./components/ClaimReview";
import "./provenance.css";

export function ClaimReviewRoute() {
  const { claimId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const handleClaimSelected = useCallback((selectedClaimId) => {
    const destination = `/provenance/review/${encodeURIComponent(selectedClaimId)}`;
    if (location.pathname !== destination) navigate(destination);
  }, [location.pathname, navigate]);

  return <ClaimReview initialClaimId={claimId} onClaimSelected={handleClaimSelected} />;
}

export function ClaimCreatorRoute() {
  const { claimCreatorSnapshot, onClaimDraftPreserved } = useOutletContext();
  const navigate = useNavigate();
  const handleClaimCreated = useCallback((createdClaim) => {
    if (createdClaim?.id) {
      navigate(`/provenance/review/${encodeURIComponent(createdClaim.id)}`);
    }
  }, [navigate]);

  return <ClaimCreator initialDraft={claimCreatorSnapshot} onDraftPreserved={onClaimDraftPreserved} onClaimCreated={handleClaimCreated} />;
}

export default function ProvenanceWorkspace() {
  const [claimCreatorSnapshot, setClaimCreatorSnapshot] = useState(null);

  const handleClaimDraftPreserved = useCallback((draft) => setClaimCreatorSnapshot(draft), []);

  return <main className="prov-shell">
    <header className="prov-header">
      <div>
        <p className="prov-eyebrow">OURANIOUS · KNOWLEDGE BASE</p>
        <h1>Provenance workspace</h1>
        <p>Record sources, propose claims, review evidence, and track resolution.</p>
      </div>
      <div className="prov-api">
        <span className="prov-live-dot" />API configured <code>/api/v1</code>
      </div>
    </header>
    <nav className="prov-tabs" aria-label="Provenance workflows">
      <NavLink to="review">Review a claim</NavLink>
      <NavLink to="claims/new">Create claim</NavLink>
      <NavLink to="sources/new">Add a source</NavLink>
    </nav>
    <Outlet context={{
      claimCreatorSnapshot,
      onClaimDraftPreserved: handleClaimDraftPreserved,
    }} />
  </main>;
}

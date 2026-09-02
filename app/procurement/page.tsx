"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

type Project = { id: string; code: string; name: string };
type BoqItem = { id: string; projectId: string; itemCode: string; element: string; description: string; quantity: string; unit: string; rate: string };
type Supplier = { id: string; code: string; name: string; contactName: string | null; email: string | null; phone: string | null; address: string | null; taxNumber: string | null; category: string | null; notes: string | null; isActive: boolean; createdAt: string; updatedAt: string };
type ProcurementStatus = "draft" | "requested" | "approved" | "ordered" | "partially_received" | "received" | "cancelled";
type PurchaseOrderItem = { id: string; purchaseOrderId: string; boqItemId: string | null; description: string; quantity: string; unit: string; unitRate: string; amount: string };
type PurchaseOrder = { id: string; projectId: string; projectCode: string; projectName: string; supplierId: string; supplierCode: string; supplierName: string; poNumber: string; status: ProcurementStatus; orderDate: string | null; expectedDeliveryDate: string | null; subtotal: string; taxAmount: string; totalAmount: string; notes: string | null; createdAt: string; updatedAt: string; items: PurchaseOrderItem[] };
type SupplierForm = { code: string; name: string; contactName: string; email: string; phone: string; address: string; taxNumber: string; category: string; notes: string; isActive: boolean };
type OrderItemForm = { boqItemId: string; description: string; quantity: string; unit: string; unitRate: string };
type OrderForm = { projectId: string; supplierId: string; poNumber: string; status: ProcurementStatus; orderDate: string; expectedDeliveryDate: string; taxRate: string; notes: string; items: OrderItemForm[] };

const statuses: ProcurementStatus[] = ["draft", "requested", "approved", "ordered", "partially_received", "received", "cancelled"];
const statusLabel: Record<ProcurementStatus, string> = { draft: "Draft", requested: "Requested", approved: "Approved", ordered: "Ordered", partially_received: "Partially received", received: "Received", cancelled: "Cancelled" };
const supplierCategories = ["Building materials", "Electrical", "Mechanical", "Plumbing", "Plant and equipment", "Professional services", "Transport and logistics", "Other"];
const emptySupplier: SupplierForm = { code: "", name: "", contactName: "", email: "", phone: "", address: "", taxNumber: "", category: "Building materials", notes: "", isActive: true };
const emptyItem: OrderItemForm = { boqItemId: "", description: "", quantity: "", unit: "No.", unitRate: "" };
const emptyOrder: OrderForm = { projectId: "", supplierId: "", poNumber: "", status: "draft", orderDate: "", expectedDeliveryDate: "", taxRate: "0", notes: "", items: [{ ...emptyItem }] };

function money(value: string | number) { const n = Number(value); return Number.isFinite(n) ? new Intl.NumberFormat(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n) : "0.00"; }
function formatDate(value: string | null) { if (!value) return "Not set"; const date = new Date(value); return Number.isNaN(date.getTime()) ? "Not set" : new Intl.DateTimeFormat(undefined, { year: "numeric", month: "short", day: "numeric" }).format(date); }
function toIso(value: string) { return value ? new Date(value).toISOString() : null; }

export default function ProcurementPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [boqItems, setBoqItems] = useState<BoqItem[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [supplierForm, setSupplierForm] = useState<SupplierForm>(emptySupplier);
  const [orderForm, setOrderForm] = useState<OrderForm>(emptyOrder);
  const [editingSupplierId, setEditingSupplierId] = useState<string | null>(null);
  const [editingOrderId, setEditingOrderId] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<"orders" | "suppliers">("orders");
  const [filterProject, setFilterProject] = useState("all");
  const [filterStatus, setFilterStatus] = useState<"all" | ProcurementStatus>("all");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const responses = await Promise.all([
        fetch("/api/projects", { cache: "no-store" }),
        fetch("/api/boq", { cache: "no-store" }),
        fetch("/api/procurement/suppliers", { cache: "no-store" }),
        fetch("/api/procurement/orders", { cache: "no-store" }),
      ]);
      const data = await Promise.all(responses.map((response) => response.json()));
      responses.forEach((response, index) => { if (!response.ok) throw new Error(data[index].error ?? "Unable to load procurement data."); });
      const projectRows = Array.isArray(data[0].data) ? data[0].data : [];
      setProjects(projectRows);
      setBoqItems(Array.isArray(data[1].data) ? data[1].data : []);
      setSuppliers(Array.isArray(data[2].data) ? data[2].data : []);
      setOrders(Array.isArray(data[3].data) ? data[3].data : []);
      if (!orderForm.projectId && projectRows[0]?.id) setOrderForm((current) => ({ ...current, projectId: projectRows[0].id }));
      if (!orderForm.supplierId) {
        const active = Array.isArray(data[2].data) ? data[2].data.find((supplier: Supplier) => supplier.isActive) : undefined;
        if (active) setOrderForm((current) => ({ ...current, supplierId: active.id }));
      }
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to load procurement data."); }
    finally { setLoading(false); }
  }, [orderForm.projectId, orderForm.supplierId]);

  useEffect(() => { void load(); }, [load]);

  const availableBoq = useMemo(() => boqItems.filter((item) => item.projectId === orderForm.projectId), [boqItems, orderForm.projectId]);
  const filteredOrders = useMemo(() => { const q = query.trim().toLowerCase(); return orders.filter((order) => { const projectMatch = filterProject === "all" || order.projectId === filterProject; const statusMatch = filterStatus === "all" || order.status === filterStatus; const text = `${order.poNumber} ${order.projectCode} ${order.projectName} ${order.supplierCode} ${order.supplierName} ${order.notes ?? ""}`.toLowerCase(); return projectMatch && statusMatch && (!q || text.includes(q)); }); }, [orders, filterProject, filterStatus, query]);
  const totalCommitted = useMemo(() => filteredOrders.filter((order) => order.status !== "cancelled").reduce((sum, order) => sum + Number(order.totalAmount || 0), 0), [filteredOrders]);
  const orderedValue = useMemo(() => orders.filter((order) => order.status === "ordered").reduce((sum, order) => sum + Number(order.totalAmount || 0), 0), [orders]);
  const receivedValue = useMemo(() => orders.filter((order) => order.status === "received").reduce((sum, order) => sum + Number(order.totalAmount || 0), 0), [orders]);

  const resetOrder = () => setOrderForm({ ...emptyOrder, projectId: projects[0]?.id ?? "", supplierId: suppliers.find((supplier) => supplier.isActive)?.id ?? "" });
  const resetSupplier = () => setSupplierForm(emptySupplier);

  const saveSupplier = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setSaving(true); setError(""); setMessage("");
    try {
      const response = await fetch(editingSupplierId ? `/api/procurement/suppliers/${editingSupplierId}` : "/api/procurement/suppliers", { method: editingSupplierId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(supplierForm) });
      const data = await response.json(); if (!response.ok) throw new Error(data.error ?? "Unable to save supplier.");
      setMessage(editingSupplierId ? "Supplier updated successfully." : "Supplier created successfully."); setEditingSupplierId(null); resetSupplier(); await load();
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to save supplier."); }
    finally { setSaving(false); }
  };

  const saveOrder = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setSaving(true); setError(""); setMessage("");
    try {
      const payload = { ...orderForm, orderDate: toIso(orderForm.orderDate), expectedDeliveryDate: toIso(orderForm.expectedDeliveryDate), taxRate: Number(orderForm.taxRate), items: orderForm.items.map((item) => ({ ...item, boqItemId: item.boqItemId || null, quantity: Number(item.quantity), unitRate: Number(item.unitRate) })) };
      const response = await fetch(editingOrderId ? `/api/procurement/orders/${editingOrderId}` : "/api/procurement/orders", { method: editingOrderId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const data = await response.json(); if (!response.ok) throw new Error(data.error ?? "Unable to save purchase order.");
      setMessage(editingOrderId ? "Purchase order updated successfully." : "Purchase order created successfully."); setEditingOrderId(null); resetOrder(); await load();
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to save purchase order."); }
    finally { setSaving(false); }
  };

  const editSupplier = (supplier: Supplier) => { setEditingSupplierId(supplier.id); setSupplierForm({ code: supplier.code, name: supplier.name, contactName: supplier.contactName ?? "", email: supplier.email ?? "", phone: supplier.phone ?? "", address: supplier.address ?? "", taxNumber: supplier.taxNumber ?? "", category: supplier.category ?? "Other", notes: supplier.notes ?? "", isActive: supplier.isActive }); setActiveSection("suppliers"); setMessage(""); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const removeSupplier = async (supplier: Supplier) => { if (!window.confirm(`Delete supplier ${supplier.name}?`)) return; setError(""); setMessage(""); try { const response = await fetch(`/api/procurement/suppliers/${supplier.id}`, { method: "DELETE" }); const data = await response.json(); if (!response.ok) throw new Error(data.error ?? "Unable to delete supplier."); setMessage("Supplier deleted successfully."); await load(); } catch (err) { setError(err instanceof Error ? err.message : "Unable to delete supplier."); } };

  const editOrder = (order: PurchaseOrder) => { setEditingOrderId(order.id); setOrderForm({ projectId: order.projectId, supplierId: order.supplierId, poNumber: order.poNumber, status: order.status, orderDate: order.orderDate ? order.orderDate.slice(0, 16) : "", expectedDeliveryDate: order.expectedDeliveryDate ? order.expectedDeliveryDate.slice(0, 16) : "", taxRate: Number(order.subtotal) ? ((Number(order.taxAmount) / Number(order.subtotal)) * 100).toFixed(2) : "0", notes: order.notes ?? "", items: order.items.length ? order.items.map((item) => ({ boqItemId: item.boqItemId ?? "", description: item.description, quantity: item.quantity, unit: item.unit, unitRate: item.unitRate })) : [{ ...emptyItem }] }); setActiveSection("orders"); setMessage(""); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const removeOrder = async (order: PurchaseOrder) => { if (!window.confirm(`Delete purchase order ${order.poNumber}?`)) return; setError(""); setMessage(""); try { const response = await fetch(`/api/procurement/orders/${order.id}`, { method: "DELETE" }); const data = await response.json(); if (!response.ok) throw new Error(data.error ?? "Unable to delete purchase order."); setMessage("Purchase order deleted successfully."); if (editingOrderId === order.id) { setEditingOrderId(null); resetOrder(); } await load(); } catch (err) { setError(err instanceof Error ? err.message : "Unable to delete purchase order."); } };

  const updateOrderItem = (index: number, patch: Partial<OrderItemForm>) => setOrderForm((current) => ({ ...current, items: current.items.map((item, itemIndex) => itemIndex === index ? { ...item, ...patch } : item) }));
  const selectBoq = (index: number, boqItemId: string) => { const boq = availableBoq.find((item) => item.id === boqItemId); updateOrderItem(index, boq ? { boqItemId, description: boq.description || boq.element, quantity: boq.quantity, unit: boq.unit, unitRate: boq.rate } : { boqItemId: "" }); };
  const addItem = () => setOrderForm((current) => ({ ...current, items: [...current.items, { ...emptyItem }] }));
  const removeItem = (index: number) => setOrderForm((current) => ({ ...current, items: current.items.length > 1 ? current.items.filter((_, itemIndex) => itemIndex !== index) : current.items }));

  const formSubtotal = orderForm.items.reduce((sum, item) => sum + (Number(item.quantity) || 0) * (Number(item.unitRate) || 0), 0);
  const formTax = formSubtotal * ((Number(orderForm.taxRate) || 0) / 100);
  const formTotal = formSubtotal + formTax;

  return (
    <main className="projects-page procurement-page">
      <header className="projects-header"><div><div className="eyebrow">Creative Studios / Procurement</div><h1>Procurement</h1><p>Connect BOQ quantities to suppliers and controlled purchase orders for project delivery.</p></div><a className="back-link" href="/">Dashboard</a></header>
      <section className="project-stats" aria-label="Procurement summary"><div className="project-stat"><span>Purchase orders</span><strong>{orders.length}</strong></div><div className="project-stat"><span>Committed value</span><strong>{money(totalCommitted)}</strong></div><div className="project-stat"><span>Ordered value</span><strong>{money(orderedValue)}</strong></div><div className="project-stat"><span>Received value</span><strong>{money(receivedValue)}</strong></div></section>
      {(error || message) && <div className={error ? "project-alert error" : "project-alert success"} role="status">{error || message}</div>}

      <div className="section-tabs" role="tablist" aria-label="Procurement sections">
        <button className={activeSection === "orders" ? "active" : ""} onClick={() => setActiveSection("orders")}>Purchase orders</button>
        <button className={activeSection === "suppliers" ? "active" : ""} onClick={() => setActiveSection("suppliers")}>Suppliers</button>
      </div>

      {activeSection === "orders" ? (
        <section className="project-layout">
          <form className="project-form" onSubmit={saveOrder}>
            <div className="section-label">{editingOrderId ? "Edit purchase order" : "New purchase order"}</div><h2>{editingOrderId ? "Update procurement order" : "Create procurement order"}</h2><p>Link purchased quantities to BOQ items where applicable. Totals are calculated server-side.</p>
            {suppliers.filter((supplier) => supplier.isActive).length === 0 ? <div className="project-empty"><strong>Add a supplier first</strong><span>Purchase orders require an active supplier.</span><button type="button" className="secondary-button" onClick={() => setActiveSection("suppliers")}>Open Suppliers</button></div> : <>
              <div className="form-grid">
                <label>Project<select value={orderForm.projectId} onChange={(event) => setOrderForm({ ...orderForm, projectId: event.target.value, items: orderForm.items.map((item) => ({ ...item, boqItemId: "" })) })} required><option value="" disabled>Select project</option>{projects.map((project) => <option key={project.id} value={project.id}>{project.code} · {project.name}</option>)}</select></label>
                <label>Supplier<select value={orderForm.supplierId} onChange={(event) => setOrderForm({ ...orderForm, supplierId: event.target.value })} required><option value="" disabled>Select supplier</option>{suppliers.filter((supplier) => supplier.isActive).map((supplier) => <option key={supplier.id} value={supplier.id}>{supplier.code} · {supplier.name}</option>)}</select></label>
                <label>PO number<input value={orderForm.poNumber} onChange={(event) => setOrderForm({ ...orderForm, poNumber: event.target.value })} placeholder="e.g. PO-2026-001" maxLength={80} required /></label>
                <label>Status<select value={orderForm.status} onChange={(event) => setOrderForm({ ...orderForm, status: event.target.value as ProcurementStatus })}>{statuses.map((status) => <option key={status} value={status}>{statusLabel[status]}</option>)}</select></label>
                <label>Order date<input type="datetime-local" value={orderForm.orderDate} onChange={(event) => setOrderForm({ ...orderForm, orderDate: event.target.value })} /></label>
                <label>Expected delivery<input type="datetime-local" value={orderForm.expectedDeliveryDate} onChange={(event) => setOrderForm({ ...orderForm, expectedDeliveryDate: event.target.value })} /></label>
                <label>Tax rate (%)<input type="number" min="0" max="100" step="0.01" value={orderForm.taxRate} onChange={(event) => setOrderForm({ ...orderForm, taxRate: event.target.value })} /></label>
                <label className="full-width">Notes<textarea value={orderForm.notes} onChange={(event) => setOrderForm({ ...orderForm, notes: event.target.value })} rows={3} maxLength={4000} placeholder="Commercial notes, delivery instructions or approval references" /></label>
              </div>
              <div className="section-label">Purchase order items</div>
              <div className="procurement-items">
                {orderForm.items.map((item, index) => <div className="procurement-item" key={`${index}-${item.boqItemId}`}>
                  <div className="item-heading"><strong>Item {index + 1}</strong>{orderForm.items.length > 1 && <button type="button" className="danger-link" onClick={() => removeItem(index)}>Remove</button>}</div>
                  <div className="form-grid">
                    <label>BOQ item<select value={item.boqItemId} onChange={(event) => selectBoq(index, event.target.value)}><option value="">Manual item</option>{availableBoq.map((boq) => <option key={boq.id} value={boq.id}>{boq.itemCode} · {boq.element}</option>)}</select></label>
                    <label>Unit<input value={item.unit} onChange={(event) => updateOrderItem(index, { unit: event.target.value })} maxLength={30} required /></label>
                    <label className="full-width">Description<textarea value={item.description} onChange={(event) => updateOrderItem(index, { description: event.target.value })} rows={2} maxLength={2000} required /></label>
                    <label>Quantity<input type="number" min="0.001" step="0.001" value={item.quantity} onChange={(event) => updateOrderItem(index, { quantity: event.target.value })} required /></label>
                    <label>Unit rate<input type="number" min="0" step="0.01" value={item.unitRate} onChange={(event) => updateOrderItem(index, { unitRate: event.target.value })} required /></label>
                    <label>Amount<input value={money((Number(item.quantity) || 0) * (Number(item.unitRate) || 0))} readOnly /></label>
                  </div>
                </div>)}
              </div>
              <button type="button" className="secondary-button" onClick={addItem}>Add item</button>
              <div className="procurement-total"><span>Subtotal <strong>{money(formSubtotal)}</strong></span><span>Tax <strong>{money(formTax)}</strong></span><span>Total <strong>{money(formTotal)}</strong></span></div>
              <div className="form-actions">{editingOrderId && <button type="button" className="secondary-button" onClick={() => { setEditingOrderId(null); resetOrder(); }}>Cancel</button>}<button type="submit" className="primary-button" disabled={saving}>{saving ? "Saving..." : editingOrderId ? "Save changes" : "Create purchase order"}</button></div>
            </>}
          </form>

          <section className="project-list-panel">
            <div className="list-toolbar"><div><div className="section-label">Purchase order register</div><h2>{filteredOrders.length} order{filteredOrders.length === 1 ? "" : "s"}</h2></div><button className="secondary-button" onClick={() => void load()} disabled={loading}>Refresh</button></div>
            <div className="filters"><input aria-label="Search purchase orders" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search PO, supplier or project" /><select value={filterProject} onChange={(event) => setFilterProject(event.target.value)}><option value="all">All projects</option>{projects.map((project) => <option key={project.id} value={project.id}>{project.code}</option>)}</select><select value={filterStatus} onChange={(event) => setFilterStatus(event.target.value as "all" | ProcurementStatus)}><option value="all">All statuses</option>{statuses.map((status) => <option key={status} value={status}>{statusLabel[status]}</option>)}</select></div>
            {loading ? <div className="project-empty"><strong>Loading procurement register...</strong><span>Reading purchase orders and supplier records.</span></div> : filteredOrders.length === 0 ? <div className="project-empty"><strong>No purchase orders found</strong><span>Create an order or change the filters.</span></div> : <div className="project-table-wrap"><table className="project-table"><thead><tr><th>PO</th><th>Project</th><th>Supplier</th><th>Items</th><th>Total</th><th>Status</th><th>Delivery</th><th>Updated</th><th /></tr></thead><tbody>{filteredOrders.map((order) => <tr key={order.id}><td><strong>{order.poNumber}</strong><div className="project-description">{formatDate(order.orderDate)}</div></td><td><strong>{order.projectCode}</strong><div className="project-description">{order.projectName}</div></td><td><strong>{order.supplierCode}</strong><div className="project-description">{order.supplierName}</div></td><td>{order.items.length}</td><td><strong>{money(order.totalAmount)}</strong><div className="project-description">Subtotal {money(order.subtotal)}</div></td><td><span className={`project-status ${order.status}`}>{statusLabel[order.status]}</span></td><td>{formatDate(order.expectedDeliveryDate)}</td><td>{formatDate(order.updatedAt)}</td><td><div className="row-actions"><button onClick={() => editOrder(order)}>Edit</button><button className="danger-link" onClick={() => void removeOrder(order)}>Delete</button></div></td></tr>)}</tbody></table></div>}
          </section>
        </section>
      ) : (
        <section className="project-layout">
          <form className="project-form" onSubmit={saveSupplier}>
            <div className="section-label">{editingSupplierId ? "Edit supplier" : "New supplier"}</div><h2>{editingSupplierId ? "Update supplier record" : "Register supplier"}</h2><p>Maintain supplier master data used by project procurement.</p>
            <div className="form-grid">
              <label>Supplier code<input value={supplierForm.code} onChange={(event) => setSupplierForm({ ...supplierForm, code: event.target.value })} placeholder="e.g. SUP-001" maxLength={50} required /></label>
              <label>Supplier name<input value={supplierForm.name} onChange={(event) => setSupplierForm({ ...supplierForm, name: event.target.value })} maxLength={200} required /></label>
              <label>Contact name<input value={supplierForm.contactName} onChange={(event) => setSupplierForm({ ...supplierForm, contactName: event.target.value })} maxLength={160} /></label>
              <label>Email<input type="email" value={supplierForm.email} onChange={(event) => setSupplierForm({ ...supplierForm, email: event.target.value })} maxLength={320} /></label>
              <label>Phone<input value={supplierForm.phone} onChange={(event) => setSupplierForm({ ...supplierForm, phone: event.target.value })} maxLength={60} /></label>
              <label>Category<select value={supplierForm.category} onChange={(event) => setSupplierForm({ ...supplierForm, category: event.target.value })}>{supplierCategories.map((category) => <option key={category}>{category}</option>)}</select></label>
              <label>Tax / registration number<input value={supplierForm.taxNumber} onChange={(event) => setSupplierForm({ ...supplierForm, taxNumber: event.target.value })} maxLength={100} /></label>
              <label className="full-width">Address<input value={supplierForm.address} onChange={(event) => setSupplierForm({ ...supplierForm, address: event.target.value })} maxLength={500} /></label>
              <label className="full-width">Notes<textarea value={supplierForm.notes} onChange={(event) => setSupplierForm({ ...supplierForm, notes: event.target.value })} rows={3} maxLength={2000} /></label>
              <label className="checkbox-field"><input type="checkbox" checked={supplierForm.isActive} onChange={(event) => setSupplierForm({ ...supplierForm, isActive: event.target.checked })} /> Active supplier</label>
            </div>
            <div className="form-actions">{editingSupplierId && <button type="button" className="secondary-button" onClick={() => { setEditingSupplierId(null); resetSupplier(); }}>Cancel</button>}<button type="submit" className="primary-button" disabled={saving}>{saving ? "Saving..." : editingSupplierId ? "Save changes" : "Add supplier"}</button></div>
          </form>
          <section className="project-list-panel">
            <div className="list-toolbar"><div><div className="section-label">Supplier register</div><h2>{suppliers.length} supplier{suppliers.length === 1 ? "" : "s"}</h2></div><button className="secondary-button" onClick={() => void load()} disabled={loading}>Refresh</button></div>
            {loading ? <div className="project-empty"><strong>Loading suppliers...</strong><span>Reading supplier master data.</span></div> : suppliers.length === 0 ? <div className="project-empty"><strong>No suppliers registered</strong><span>Add your first supplier to begin procurement.</span></div> : <div className="project-table-wrap"><table className="project-table"><thead><tr><th>Code</th><th>Supplier</th><th>Contact</th><th>Category</th><th>Phone</th><th>Status</th><th>Updated</th><th /></tr></thead><tbody>{suppliers.map((supplier) => <tr key={supplier.id}><td><strong>{supplier.code}</strong></td><td><div className="project-name">{supplier.name}</div><div className="project-description">{supplier.address ?? "No address"}</div></td><td>{supplier.contactName ?? "Not set"}<div className="project-description">{supplier.email ?? "No email"}</div></td><td>{supplier.category ?? "Other"}</td><td>{supplier.phone ?? "Not set"}</td><td><span className={`project-status ${supplier.isActive ? "completed" : "cancelled"}`}>{supplier.isActive ? "Active" : "Inactive"}</span></td><td>{formatDate(supplier.updatedAt)}</td><td><div className="row-actions"><button onClick={() => editSupplier(supplier)}>Edit</button><button className="danger-link" onClick={() => void removeSupplier(supplier)}>Delete</button></div></td></tr>)}</tbody></table></div>}
          </section>
        </section>
      )}
    </main>
  );
}

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from documents.models import Document
from documents.serializers import DocumentSerializer
from documents.storage import upload_file


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by("-uploaded_at")
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        VALID_DOC_TYPES = {"JOB", "INVOICE", "RECEIPT"}

        doc_type = (request.data.get("doc_type") or "").strip().upper()
        if doc_type not in VALID_DOC_TYPES:
            return Response({"detail": "doc_type must be one of JOB, INVOICE, RECEIPT"}, status=400)

        job_id = request.data.get("job_id")
        invoice_id = request.data.get("invoice_id")
        receipt_id = request.data.get("receipt_id")

        required = {
            "JOB": ("job_id", job_id),
            "INVOICE": ("invoice_id", invoice_id),
            "RECEIPT": ("receipt_id", receipt_id),
        }
        field_name, value = required[doc_type]
        if not value:
            return Response({"detail": f"{field_name} required for {doc_type} document"}, status=400)

        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"detail": "file is required"}, status=400)

        folder = f"documents/{doc_type.lower()}/{value}"
        uploaded = upload_file(file_obj, folder=folder)

        document = Document.objects.create(
            doc_type=doc_type,
            job_id=job_id if doc_type == "JOB" else None,
            invoice_id=invoice_id if doc_type == "INVOICE" else None,
            receipt_id=receipt_id if doc_type == "RECEIPT" else None,
            filename=file_obj.name,
            content_type=getattr(file_obj, "content_type", "") or "",
            size_bytes=getattr(file_obj, "size", 0) or 0,
            storage_provider="cloudinary",
            storage_key=uploaded["public_id"],
            url=uploaded["url"],
            uploaded_by=request.user,
        )

        serializer = self.get_serializer(document)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    @action(detail=False, methods=["get"])
    def by_job(self, request):
        job_id = request.query_params.get("job_id")
        return Response(DocumentSerializer(self.queryset.filter(job_id=job_id), many=True).data)

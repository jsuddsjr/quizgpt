import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseServerError
from django.views import View
from .models import DragQuestion, PaperQuestion, Paper
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator


class PaperQuestionReorder(View):
    template_name = "paper_question_reorder.tmpl"

    # Ensure we have a CSRF cookie set
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, pk):
        return render(
            self.request,
            self.template_name,
            {
                "pk": pk,
                "questions": DragQuestion.objects.filter(paperquestion__paper_id=pk).order_by("paperquestion__order"),
                "paper": Paper.objects.get(id=pk),
            },
        )

    # Process POST AJAX Request
    def post(self, request, pk):
        if request.method == "POST" and request.is_ajax():
            try:
                # Parse the JSON payload
                data = json.loads(request.body)[0]
                # Loop over our list order. The id equals the question id. Update the order and save
                for idx, question in enumerate(data):
                    pq = PaperQuestion.objects.get(paper=pk, question=question["id"])
                    pq.order = idx + 1
                    pq.save()

            except KeyError:
                HttpResponseServerError("Malformed data!")

            return JsonResponse({"success": True}, status=200)
        else:
            return JsonResponse({"success": False}, status=400)

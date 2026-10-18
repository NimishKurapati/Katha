from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import Novel, Chapter, Rating, Wishlist, ReadingHistory, WriterRequest
from .forms import NovelForm, ChapterForm, WriterRequestForm


def is_approved_writer(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return WriterRequest.objects.filter(user=user, status='approved').exists()


def home(request):
    novels = Novel.objects.all().order_by('-created_at')
    user_wishlist = []
    if request.user.is_authenticated:
        user_wishlist = Wishlist.objects.filter(
            user=request.user).values_list('novel_id', flat=True)

    return render(request, 'novels/home.html', {
        'novels': novels,
        'user_wishlist': user_wishlist
    })


def read_novel(request, novel_id, chapter_num=None):
    novel = get_object_or_404(Novel, id=novel_id)
    chapters = novel.chapters.all()

    user_rating = None
    if request.user.is_authenticated:
        ReadingHistory.objects.update_or_create(user=request.user, novel=novel)
        rating_obj = Rating.objects.filter(
            user=request.user, novel=novel).first()
        if rating_obj:
            user_rating = rating_obj.score

    current_chapter = None
    if chapter_num:
        current_chapter = get_object_or_404(
            Chapter, novel=novel, chapter_number=chapter_num)
    elif chapters.exists():
        current_chapter = chapters.first()

    return render(request, 'novels/read_novel.html', {
        'novel': novel,
        'chapters': chapters,
        'current_chapter': current_chapter,
        'user_rating': user_rating,
    })


@login_required
def rate_novel(request, novel_id):
    if request.method == 'POST':
        novel = get_object_or_404(Novel, id=novel_id)
        try:
            score = int(request.POST.get('score', 0))
        except ValueError:
            score = 0

        if 1 <= score <= 5:
            Rating.objects.update_or_create(
                user=request.user,
                novel=novel,
                defaults={'score': score}
            )
            messages.success(
                request, f"You rated {novel.title} {score}/5 stars!")
    return redirect('read_novel', novel_id=novel_id)


@login_required
def toggle_wishlist(request, novel_id):
    novel = get_object_or_404(Novel, id=novel_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user, novel=novel)

    if not created:
        wishlist_item.delete()
        messages.info(request, f"Removed '{novel.title}' from your wishlist.")
    else:
        messages.success(request, f"Added '{novel.title}' to your wishlist!")

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def my_novels(request):
    history = ReadingHistory.objects.filter(
        user=request.user).select_related('novel')
    return render(request, 'novels/my_novels.html', {'history': history})


@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(
        user=request.user).select_related('novel')
    return render(request, 'novels/wishlist.html', {'wishlist': wishlist})


@login_required
def writer_dashboard(request):
    approved = is_approved_writer(request.user)

    # Case 1: User is an Approved Writer (or Admin)
    if approved:
        my_published_novels = Novel.objects.filter(
            author=request.user).order_by('-created_at')
        if request.method == 'POST':
            form = NovelForm(request.POST)
            if form.is_valid():
                novel = form.save(commit=False)
                novel.author = request.user
                novel.save()
                messages.success(
                    request, "Novel published! Now you can add chapters.")
                return redirect('writer_dashboard')
        else:
            form = NovelForm()

        return render(request, 'novels/writer_dashboard.html', {
            'approved': True,
            'novels': my_published_novels,
            'form': form
        })

    # Case 2: User is NOT Approved Yet -> Show Request Status or Application Form
    writer_req = WriterRequest.objects.filter(user=request.user).first()
    if request.method == 'POST':
        req_form = WriterRequestForm(request.POST, instance=writer_req)
        if req_form.is_valid():
            new_req = req_form.save(commit=False)
            new_req.user = request.user
            new_req.status = 'pending'
            new_req.save()
            messages.success(
                request, "Your Writer Request has been sent to the admins!")
            return redirect('writer_dashboard')
    else:
        req_form = WriterRequestForm(instance=writer_req)

    return render(request, 'novels/writer_dashboard.html', {
        'approved': False,
        'writer_req': writer_req,
        'req_form': req_form
    })


@login_required
def add_chapter(request, novel_id):
    if not is_approved_writer(request.user):
        messages.error(
            request, "You must be an approved writer to publish chapters.")
        return redirect('writer_dashboard')

    novel = get_object_or_404(Novel, id=novel_id, author=request.user)

    if request.method == 'POST':
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter_num = form.cleaned_data['chapter_number']
            if Chapter.objects.filter(novel=novel, chapter_number=chapter_num).exists():
                form.add_error(
                    'chapter_number', f'Chapter {chapter_num} already exists for this novel.')
            else:
                chapter = form.save(commit=False)
                chapter.novel = novel
                chapter.save()
                messages.success(
                    request, f"Chapter {chapter.chapter_number} published!")
                return redirect('writer_dashboard')
    else:
        last_chapter = novel.chapters.order_by('-chapter_number').first()
        next_chapter_num = (last_chapter.chapter_number +
                            1) if last_chapter else 1
        form = ChapterForm(initial={'chapter_number': next_chapter_num})

    return render(request, 'novels/add_chapter.html', {
        'novel': novel,
        'form': form
    })


@login_required
def manage_writer_requests(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admins only.")
        return redirect('home')

    requests_list = WriterRequest.objects.select_related(
        'user').order_by('-created_at')
    return render(request, 'novels/manage_requests.html', {
        'requests_list': requests_list
    })


@login_required
def process_writer_request(request, req_id, action):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admins only.")
        return redirect('home')

    if request.method == 'POST':
        writer_req = get_object_or_404(WriterRequest, id=req_id)
        if action == 'approve':
            writer_req.status = 'approved'
            writer_req.save()
            messages.success(
                request, f"Approved {writer_req.user.username} as a Writer!")
        elif action == 'reject':
            writer_req.status = 'rejected'
            writer_req.save()
            messages.warning(
                request, f"Rejected writer request from {writer_req.user.username}.")

    return redirect('manage_writer_requests')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
